import re
from typing import List, Dict, Tuple, Any

def mask_email(email_body: str) -> Tuple[str, List[Dict[str, Any]]]:
    
    
    # Regex for Credit/Debit Card Numbers (13-16 digits, with or without spaces/hyphens)
    credit_card_pattern = re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b') 

    # Regex for Aadhar Card Number (12 digits, often grouped as XXXX XXXX XXXX)
    aadhar_pattern = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')

    # Regex for Phone Numbers (common international/Indian/UK formats)
    phone_pattern = re.compile(
        r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        r'|' # OR
        r'\b\d{5}\s\d{6}\b'
        r'|' # OR
        r'\b\d{10,11}\b'
    )

    # Regex for Email Addresses
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    # OR a 2-digit year (typically 20-99, for years like '25', '99' etc. to avoid matching days like '15')
    card_expiry_pattern = re.compile(r'\b(?:0[1-9]|1[0-2])[-/](?:[12]\d{3}|[2-9]\d)\b')

    # Regex for Date of Birth (common formats: DD-MM-YYYY, MM/DD/YYYY)
    dob_pattern = re.compile(r'\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b')

    # Regex for CVV (3 or 4 digits) - NOW CONTEXT-DEPENDENT
    cvv_pattern = re.compile(r'\b(?:CVV|CVC|Security Code|CSC|CID)\s*(\d{3,4})\b', re.IGNORECASE)

    # Regex for Full Name (using contextual pattern: "My name is John Doe")
    name_context_pattern = re.compile(r'(?:My name is |Mr\. |Ms\. |Dr\. |Prof\. )([A-Z][a-z]+(?: [A-Z][a-z]+(?: [A-Z][a-z]+)?)?)')
    
    # Define the order of processing for patterns. More specific/longer patterns first.
    patterns_to_check = [
        {'name': 'credit_debit_card_number', 'pattern': credit_card_pattern, 'placeholder': '[credit_debit_card_number]'},
        {'name': 'aadhar_card_number', 'pattern': aadhar_pattern, 'placeholder': '[aadhar_card_number]'},
        {'name': 'phone_number', 'pattern': phone_pattern, 'placeholder': '[phone_number]'},
        {'name': 'email', 'pattern': email_pattern, 'placeholder': '[email]'},
        {'name': 'card_expiry_number', 'pattern': card_expiry_pattern, 'placeholder': '[card_expiry_number]'},
        {'name': 'dob', 'pattern': dob_pattern, 'placeholder': '[dob]'},
        {'name': 'cvv_number', 'pattern': cvv_pattern, 'placeholder': '[cvv_number]'},
        {'name': 'full_name', 'pattern': name_context_pattern, 'placeholder': '[full_name]'},
    ]

    all_potential_pii_matches = [] 

    # First pass: Find all potential PII entities with their original spans
    for pii_type_info in patterns_to_check:
        pattern = pii_type_info['pattern']
        classification = pii_type_info['name']
        placeholder = pii_type_info['placeholder']

        for match in pattern.finditer(email_body):
            start, end = match.span()
            entity_value = match.group(0) 

            # Special handling for full_name and cvv_number where the actual entity is in group 1
            if classification == 'full_name' or classification == 'cvv_number':
                if match.group(1): # Ensure group 1 exists for contextual matches
                    entity_value = match.group(1)
                    # Adjust start/end to reflect the actual group(1) span within the original email_body
                    actual_entity_start_in_body = email_body.find(entity_value, start, end)
                    if actual_entity_start_in_body != -1:
                        start = actual_entity_start_in_body
                        end = actual_entity_start_in_body + len(entity_value)
                    else: # Fallback if precise span not found
                        entity_value = match.group(0)
                        start, end = match.span()
                else: # Fallback if group 1 is empty/not found
                    entity_value = match.group(0)
                    start, end = match.span()


            all_potential_pii_matches.append({
                'start': start,
                'end': end,
                'classification': classification,
                'entity': entity_value,
                'placeholder': placeholder,
                'original_match_text': match.group(0) # Store full matched text for debug/priority
            })

    # Second pass: Filter out overlapping matches, prioritizing longer and earlier matches
    all_potential_pii_matches.sort(key=lambda x: (x['start'], -(x['end'] - x['start'])))

    final_unique_pii_to_mask = []
    masked_intervals = []

    for pii_info in all_potential_pii_matches:
        current_start = pii_info['start']
        current_end = pii_info['end']
        
        is_covered_by_existing = False
        for masked_start, masked_end in masked_intervals:
            if max(current_start, masked_start) < min(current_end, masked_end):
                is_covered_by_existing = True
                break
        
        if not is_covered_by_existing:
            final_unique_pii_to_mask.append(pii_info)
            masked_intervals.append((current_start, current_end))
            masked_intervals.sort()

    # Third pass: Construct the masked email and the final masked entities list
    final_unique_pii_to_mask.sort(key=lambda x: x['start'])

    masked_email_parts = []
    current_idx = 0
    final_masked_entities_for_output = []

    for pii_info in final_unique_pii_to_mask:
        start = pii_info['start']
        end = pii_info['end']

        masked_email_parts.append(email_body[current_idx:start])
        masked_email_parts.append(pii_info['placeholder'])

        final_masked_entities_for_output.append({
            "position": [start, end],
            "classification": pii_info['classification'],
            "entity": pii_info['entity']
        })
        current_idx = end

    masked_email_parts.append(email_body[current_idx:])
    
    masked_email = "".join(masked_email_parts)
    
    final_masked_entities_for_output.sort(key=lambda x: x['position'][0])

    return masked_email, final_masked_entities_for_output

def demask_email(masked_email: str, masked_entities_list: List[Dict[str, Any]]) -> str:
    reconstructed_email = masked_email

    masked_entities_list.sort(key=lambda x: x['position'][0], reverse=True)

    for entity_info in masked_entities_list:
        original_entity = entity_info['entity']
        classification = entity_info['classification']
        
        placeholder_text = f"[{classification}]"

        if placeholder_text in reconstructed_email:
            reconstructed_email = reconstructed_email.replace(placeholder_text, original_entity, 1)

    return reconstructed_email
