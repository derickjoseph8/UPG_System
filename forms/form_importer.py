"""
Form Import Service
Handles importing forms from JSON, XML (XLSForm), and KoboToolbox formats.
Preserves the original structure including sections and groups.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional
import re


class FormImporter:
    """
    Import forms from various formats into UPG FormTemplate structure.
    Supports:
    - JSON (UPG internal format)
    - XLSForm JSON (KoboToolbox format)
    - XML (ODK/XLSForm XML format)
    """

    # Reverse mapping from XLSForm types to UPG types
    XLSFORM_TO_UPG_TYPE = {
        'text': 'text',
        'integer': 'number',
        'decimal': 'decimal',
        'date': 'date',
        'time': 'time',
        'datetime': 'datetime',
        'geopoint': 'location',
        'geotrace': 'location',
        'geoshape': 'location',
        'image': 'image',
        'audio': 'audio',
        'video': 'video',
        'file': 'file',
        'barcode': 'barcode',
        'note': 'note',
        'calculate': 'calculate',
        'acknowledge': 'boolean',
        'range': 'range',
        'rank': 'select',
    }

    def __init__(self):
        self.errors = []
        self.warnings = []

    def import_from_json(self, json_data: str) -> Tuple[Dict, List[Dict]]:
        """
        Import form from JSON format.
        Supports both UPG internal format and XLSForm JSON format.

        Args:
            json_data: JSON string

        Returns:
            tuple: (form_metadata, fields_list)
        """
        self.errors = []
        self.warnings = []

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON format: {str(e)}")
            return None, []

        # Detect format type
        if 'survey' in data:
            # XLSForm JSON format (from KoboToolbox)
            return self._parse_xlsform_json(data)
        elif 'fields' in data or 'form_fields' in data:
            # UPG internal format
            return self._parse_upg_json(data)
        else:
            # Try to parse as generic form definition
            return self._parse_generic_json(data)

    def import_from_xml(self, xml_data: str) -> Tuple[Dict, List[Dict]]:
        """
        Import form from XML format (ODK/XLSForm XML).

        Args:
            xml_data: XML string

        Returns:
            tuple: (form_metadata, fields_list)
        """
        self.errors = []
        self.warnings = []

        try:
            # Remove BOM if present
            xml_data = xml_data.lstrip('\ufeff')
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            self.errors.append(f"Invalid XML format: {str(e)}")
            return None, []

        return self._parse_xform_xml(root)

    def import_from_kobo_asset(self, asset_data: Dict) -> Tuple[Dict, List[Dict]]:
        """
        Import form directly from KoboToolbox asset API response.

        Args:
            asset_data: API response from KoboToolbox asset endpoint

        Returns:
            tuple: (form_metadata, fields_list)
        """
        self.errors = []
        self.warnings = []

        # Extract content (XLSForm structure)
        content = asset_data.get('content', {})
        if not content:
            self.errors.append("No content found in KoboToolbox asset")
            return None, []

        # Get metadata
        metadata = {
            'name': asset_data.get('name', 'Imported Form'),
            'description': asset_data.get('settings', {}).get('description', ''),
            'kobo_asset_uid': asset_data.get('uid'),
            'kobo_form_url': asset_data.get('deployment__links', {}).get('url', ''),
        }

        # Parse the XLSForm content
        form_meta, fields = self._parse_xlsform_json(content)

        # Merge metadata
        form_meta.update(metadata)

        return form_meta, fields

    def _parse_xlsform_json(self, data: Dict) -> Tuple[Dict, List[Dict]]:
        """Parse XLSForm JSON format (KoboToolbox)"""
        survey = data.get('survey', [])
        choices = data.get('choices', [])
        settings = data.get('settings', {})

        # Build choices lookup
        choices_lookup = {}
        for choice in choices:
            list_name = choice.get('list_name', '')
            if list_name not in choices_lookup:
                choices_lookup[list_name] = []
            choices_lookup[list_name].append({
                'value': choice.get('name', ''),
                'label': choice.get('label', choice.get('name', ''))
            })

        # Form metadata
        metadata = {
            'name': settings.get('form_title', 'Imported Form'),
            'description': settings.get('form_id', ''),
            'form_type': 'custom_form',
            'status': 'draft',
        }

        # Parse fields
        fields = []
        order = 0
        group_stack = []  # Track nested groups

        for row in survey:
            row_type = row.get('type', '').lower()

            # Skip metadata fields
            if row_type in ['start', 'end', 'deviceid', 'phonenumber', 'username', 'simserial', 'subscriberid', 'today']:
                continue

            # Handle group start
            if row_type == 'begin_group' or row_type == 'begin group':
                group_name = row.get('name', f'group_{order}')
                group_label = row.get('label', group_name)

                # Add section field
                fields.append({
                    'field_name': group_name,
                    'field_label': group_label,
                    'field_type': 'section',
                    'required': False,
                    'help_text': row.get('hint', ''),
                    'order': order,
                    'choices': [],
                })
                order += 1
                group_stack.append(group_name)
                continue

            # Handle group end
            if row_type == 'end_group' or row_type == 'end group':
                if group_stack:
                    group_stack.pop()
                continue

            # Handle repeat (treat as group for now)
            if row_type == 'begin_repeat' or row_type == 'begin repeat':
                repeat_name = row.get('name', f'repeat_{order}')
                repeat_label = row.get('label', repeat_name)

                fields.append({
                    'field_name': repeat_name,
                    'field_label': f"[Repeat] {repeat_label}",
                    'field_type': 'group',
                    'required': False,
                    'help_text': row.get('hint', ''),
                    'order': order,
                    'choices': [],
                })
                order += 1
                group_stack.append(repeat_name)
                continue

            if row_type == 'end_repeat' or row_type == 'end repeat':
                if group_stack:
                    group_stack.pop()
                continue

            # Parse regular field
            field = self._parse_xlsform_field(row, choices_lookup, order)
            if field:
                fields.append(field)
                order += 1

        return metadata, fields

    def _parse_xlsform_field(self, row: Dict, choices_lookup: Dict, order: int) -> Optional[Dict]:
        """Parse a single XLSForm field row"""
        row_type = row.get('type', '').lower().strip()
        name = row.get('name', f'field_{order}')
        label = row.get('label', name)

        # Handle select_one and select_multiple
        field_type = 'text'
        choices = []

        if row_type.startswith('select_one ') or row_type.startswith('select one '):
            field_type = 'select'
            list_name = row_type.split(' ', 1)[1].strip()
            choices = choices_lookup.get(list_name, [])
        elif row_type.startswith('select_multiple ') or row_type.startswith('select multiple '):
            field_type = 'checkbox'
            list_name = row_type.split(' ', 1)[1].strip()
            choices = choices_lookup.get(list_name, [])
        elif row_type == 'select_one yes_no' or row_type == 'select one yes_no':
            field_type = 'boolean'
        else:
            # Map standard types
            field_type = self.XLSFORM_TO_UPG_TYPE.get(row_type, 'text')

        # Parse constraints for validation
        min_value = None
        max_value = None
        min_length = None
        max_length = None

        constraint = row.get('constraint', '')
        if constraint:
            # Parse numeric constraints
            min_match = re.search(r'\.\s*>=?\s*(-?\d+\.?\d*)', constraint)
            max_match = re.search(r'\.\s*<=?\s*(-?\d+\.?\d*)', constraint)
            if min_match:
                try:
                    min_value = float(min_match.group(1))
                except ValueError:
                    pass
            if max_match:
                try:
                    max_value = float(max_match.group(1))
                except ValueError:
                    pass

            # Parse string length constraints
            len_min_match = re.search(r'string-length\(\.\)\s*>=?\s*(\d+)', constraint)
            len_max_match = re.search(r'string-length\(\.\)\s*<=?\s*(\d+)', constraint)
            if len_min_match:
                min_length = int(len_min_match.group(1))
            if len_max_match:
                max_length = int(len_max_match.group(1))

        # Parse conditional display (relevant)
        show_if_field = ''
        show_if_value = ''
        relevant = row.get('relevant', '')
        if relevant:
            # Parse simple conditions like "${field} = 'value'"
            rel_match = re.search(r'\$\{(\w+)\}\s*=\s*[\'"]?([^\'"}\s]+)[\'"]?', relevant)
            if rel_match:
                show_if_field = rel_match.group(1)
                show_if_value = rel_match.group(2)

        return {
            'field_name': name,
            'field_label': label,
            'field_type': field_type,
            'required': row.get('required', '').lower() == 'yes',
            'help_text': row.get('hint', ''),
            'placeholder': row.get('placeholder', ''),
            'default_value': row.get('default', ''),
            'choices': choices,
            'min_value': min_value,
            'max_value': max_value,
            'min_length': min_length,
            'max_length': max_length,
            'show_if_field': show_if_field,
            'show_if_value': show_if_value,
            'order': order,
        }

    def _parse_upg_json(self, data: Dict) -> Tuple[Dict, List[Dict]]:
        """Parse UPG internal JSON format"""
        metadata = {
            'name': data.get('name', 'Imported Form'),
            'description': data.get('description', ''),
            'form_type': data.get('form_type', 'custom_form'),
            'status': 'draft',
            'form_purpose': data.get('form_purpose', 'general'),
        }

        # Get fields from either 'fields' or 'form_fields' key
        fields_data = data.get('fields', data.get('form_fields', []))
        fields = []

        for order, field_data in enumerate(fields_data):
            field = {
                'field_name': field_data.get('name', field_data.get('field_name', f'field_{order}')),
                'field_label': field_data.get('label', field_data.get('field_label', 'Untitled')),
                'field_type': field_data.get('type', field_data.get('field_type', 'text')),
                'required': field_data.get('required', False),
                'help_text': field_data.get('helpText', field_data.get('help_text', '')),
                'placeholder': field_data.get('placeholder', ''),
                'default_value': field_data.get('defaultValue', field_data.get('default_value', '')),
                'choices': field_data.get('choices', field_data.get('options', [])),
                'min_value': field_data.get('validation', {}).get('min', field_data.get('min_value')),
                'max_value': field_data.get('validation', {}).get('max', field_data.get('max_value')),
                'min_length': field_data.get('min_length'),
                'max_length': field_data.get('max_length'),
                'show_if_field': field_data.get('showIfField', field_data.get('show_if_field', '')),
                'show_if_value': field_data.get('showIfValue', field_data.get('show_if_value', '')),
                'order': order,
            }
            fields.append(field)

        return metadata, fields

    def _parse_generic_json(self, data: Dict) -> Tuple[Dict, List[Dict]]:
        """Parse generic JSON format (best effort)"""
        metadata = {
            'name': data.get('title', data.get('name', 'Imported Form')),
            'description': data.get('description', ''),
            'form_type': 'custom_form',
            'status': 'draft',
        }

        # Try to find fields in various locations
        fields_data = (
            data.get('fields') or
            data.get('questions') or
            data.get('items') or
            data.get('elements') or
            []
        )

        if not fields_data:
            self.warnings.append("No fields found in JSON. Form imported with no fields.")
            return metadata, []

        fields = []
        for order, item in enumerate(fields_data):
            if isinstance(item, dict):
                field = {
                    'field_name': item.get('name', item.get('id', f'field_{order}')),
                    'field_label': item.get('label', item.get('title', item.get('question', 'Untitled'))),
                    'field_type': self._guess_field_type(item),
                    'required': item.get('required', False),
                    'help_text': item.get('hint', item.get('description', '')),
                    'choices': item.get('choices', item.get('options', [])),
                    'order': order,
                }
                fields.append(field)

        return metadata, fields

    def _guess_field_type(self, item: Dict) -> str:
        """Guess field type from item properties"""
        item_type = str(item.get('type', '')).lower()

        type_mapping = {
            'string': 'text',
            'str': 'text',
            'text': 'text',
            'textarea': 'textarea',
            'long_text': 'textarea',
            'number': 'number',
            'int': 'number',
            'integer': 'number',
            'float': 'decimal',
            'decimal': 'decimal',
            'date': 'date',
            'time': 'time',
            'datetime': 'datetime',
            'email': 'email',
            'phone': 'phone',
            'tel': 'phone',
            'select': 'select',
            'dropdown': 'select',
            'choice': 'select',
            'radio': 'radio',
            'checkbox': 'checkbox',
            'multi': 'checkbox',
            'multiple': 'checkbox',
            'boolean': 'boolean',
            'bool': 'boolean',
            'yes_no': 'boolean',
            'yesno': 'boolean',
            'file': 'file',
            'image': 'image',
            'photo': 'image',
            'audio': 'audio',
            'video': 'video',
            'location': 'location',
            'gps': 'location',
            'geopoint': 'location',
            'signature': 'signature',
            'rating': 'rating',
            'section': 'section',
            'group': 'group',
        }

        return type_mapping.get(item_type, 'text')

    def _parse_xform_xml(self, root: ET.Element) -> Tuple[Dict, List[Dict]]:
        """Parse ODK/XForm XML format"""
        # Handle namespaces
        ns = {
            'h': 'http://www.w3.org/1999/xhtml',
            'xf': 'http://www.w3.org/2002/xforms',
            'jr': 'http://openrosa.org/javarosa',
        }

        # Try to find the model and body
        # XForms can have different structures

        metadata = {
            'name': 'Imported XML Form',
            'description': '',
            'form_type': 'custom_form',
            'status': 'draft',
        }

        fields = []

        # Try to get title
        title = root.find('.//h:title', ns) or root.find('.//title')
        if title is not None and title.text:
            metadata['name'] = title.text

        # Find the body/form content
        body = root.find('.//h:body', ns) or root.find('.//body') or root

        # Process all input elements
        order = 0
        for elem in body.iter():
            tag = elem.tag.split('}')[-1].lower()  # Remove namespace

            field = None

            if tag == 'input':
                field = self._parse_xml_input(elem, ns, order)
            elif tag == 'select1':
                field = self._parse_xml_select(elem, ns, order, multiple=False)
            elif tag == 'select':
                field = self._parse_xml_select(elem, ns, order, multiple=True)
            elif tag == 'upload':
                field = self._parse_xml_upload(elem, ns, order)
            elif tag == 'group':
                field = self._parse_xml_group(elem, ns, order)

            if field:
                fields.append(field)
                order += 1

        if not fields:
            self.warnings.append("No fields could be parsed from XML. The XML format may not be supported.")

        return metadata, fields

    def _parse_xml_input(self, elem: ET.Element, ns: Dict, order: int) -> Dict:
        """Parse XML input element"""
        ref = elem.get('ref', f'/data/field_{order}')
        name = ref.split('/')[-1]

        label = ''
        label_elem = elem.find('.//label') or elem.find('.//{http://www.w3.org/2002/xforms}label')
        if label_elem is not None and label_elem.text:
            label = label_elem.text

        hint = ''
        hint_elem = elem.find('.//hint') or elem.find('.//{http://www.w3.org/2002/xforms}hint')
        if hint_elem is not None and hint_elem.text:
            hint = hint_elem.text

        # Guess type from appearance or other attributes
        appearance = elem.get('appearance', '')
        field_type = 'text'
        if 'numbers' in appearance or 'numeric' in appearance:
            field_type = 'number'
        elif 'signature' in appearance:
            field_type = 'signature'

        return {
            'field_name': name,
            'field_label': label or name,
            'field_type': field_type,
            'required': False,
            'help_text': hint,
            'choices': [],
            'order': order,
        }

    def _parse_xml_select(self, elem: ET.Element, ns: Dict, order: int, multiple: bool) -> Dict:
        """Parse XML select/select1 element"""
        ref = elem.get('ref', f'/data/field_{order}')
        name = ref.split('/')[-1]

        label = ''
        label_elem = elem.find('.//label') or elem.find('.//{http://www.w3.org/2002/xforms}label')
        if label_elem is not None and label_elem.text:
            label = label_elem.text

        # Get choices
        choices = []
        for item in elem.findall('.//item') + elem.findall('.//{http://www.w3.org/2002/xforms}item'):
            value_elem = item.find('.//value') or item.find('.//{http://www.w3.org/2002/xforms}value')
            item_label_elem = item.find('.//label') or item.find('.//{http://www.w3.org/2002/xforms}label')

            value = value_elem.text if value_elem is not None and value_elem.text else ''
            item_label = item_label_elem.text if item_label_elem is not None and item_label_elem.text else value

            if value:
                choices.append({'value': value, 'label': item_label})

        return {
            'field_name': name,
            'field_label': label or name,
            'field_type': 'checkbox' if multiple else 'select',
            'required': False,
            'help_text': '',
            'choices': choices,
            'order': order,
        }

    def _parse_xml_upload(self, elem: ET.Element, ns: Dict, order: int) -> Dict:
        """Parse XML upload element"""
        ref = elem.get('ref', f'/data/field_{order}')
        name = ref.split('/')[-1]
        mediatype = elem.get('mediatype', '')

        label = ''
        label_elem = elem.find('.//label') or elem.find('.//{http://www.w3.org/2002/xforms}label')
        if label_elem is not None and label_elem.text:
            label = label_elem.text

        field_type = 'file'
        if 'image' in mediatype:
            field_type = 'image'
        elif 'audio' in mediatype:
            field_type = 'audio'
        elif 'video' in mediatype:
            field_type = 'video'

        return {
            'field_name': name,
            'field_label': label or name,
            'field_type': field_type,
            'required': False,
            'help_text': '',
            'choices': [],
            'order': order,
        }

    def _parse_xml_group(self, elem: ET.Element, ns: Dict, order: int) -> Dict:
        """Parse XML group element"""
        ref = elem.get('ref', f'/data/group_{order}')
        name = ref.split('/')[-1]

        label = ''
        label_elem = elem.find('.//label') or elem.find('.//{http://www.w3.org/2002/xforms}label')
        if label_elem is not None and label_elem.text:
            label = label_elem.text

        return {
            'field_name': name,
            'field_label': label or name,
            'field_type': 'section',
            'required': False,
            'help_text': '',
            'choices': [],
            'order': order,
        }


def import_form_from_file(file_content: str, file_type: str) -> Tuple[Optional[Dict], List[Dict], List[str], List[str]]:
    """
    Convenience function to import form from file content.

    Args:
        file_content: File content as string
        file_type: 'json' or 'xml'

    Returns:
        tuple: (metadata, fields, errors, warnings)
    """
    importer = FormImporter()

    if file_type.lower() == 'json':
        metadata, fields = importer.import_from_json(file_content)
    elif file_type.lower() in ['xml', 'xform']:
        metadata, fields = importer.import_from_xml(file_content)
    else:
        importer.errors.append(f"Unsupported file type: {file_type}")
        return None, [], importer.errors, importer.warnings

    return metadata, fields, importer.errors, importer.warnings
