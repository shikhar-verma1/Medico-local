from presidio_analyzer import AnalyzerEngine,PatternRecognizer,Pattern
from presidio_anonymizer import AnonymizerEngine ,OperatorConfig
import json
def anonymize_vault():
    raw_clinical_note = """Patient: John Doe
                DOB: 05/12/1985
                Age: 45
                Gender: Male
                Phone: 555-019-8472
                Address: 21 B-baker street London
                Chief Complaint: Mr. Doe arrived at the clinic on Tuesday complaining of 
                severe chest pain. 
                He mentioned his brother, Michael Doe, had similar symptoms last year."""
    print("---original_raw_data---")
    print(raw_clinical_note)
    print("Initializing the local engine ")

    analyzer =AnalyzerEngine()

    age_pattern = Pattern(name="age_pattern", regex=r"Age:\s*\d+", score=1.0)
    analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="AGE", patterns=[age_pattern]))

    gender_pattern = Pattern(name="gender_pattern", regex=r"Gender:\s*[a-zA-Z]+", score=1.0)
    analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="GENDER", patterns=[gender_pattern]))

    address_pattern = Pattern(name="address_pattern", regex=r"\d+\s+[a-zA-Z\-\s]+street", score=1.0)
    analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="STREET_ADDRESS", patterns=[address_pattern]))
    
    anonymizer = AnonymizerEngine()

    custom_operators = {
        "AGE": OperatorConfig("replace", {"new_value": "<AGE>"}),
        "GENDER": OperatorConfig("replace", {"new_value": "<GENDER>"}),
        "STREET_ADDRESS": OperatorConfig("replace", {"new_value": "<STREET_ADDRESS>"}),
        
    }

    detected_pii = analyzer.analyze(
        text = raw_clinical_note,
        entities = ["PERSON","PHONE_NUMBER","DATE_TIME","LOCATION","GENDER","AGE","STREET_ADDRESS"],
        language="en"
    )
    patient_vault = {}
    vault_counter = 0
    anonymized_text = raw_clinical_note
    sorted_result = sorted(detected_pii,key=lambda x:x.start ,reverse =True)
    for result in sorted_result:
        entity_type = result.entity_type
        original_value = raw_clinical_note[result.start:result.end]
        normalized_value = original_value.strip().lower()

        if normalized_value not in patient_vault:
            vault_counter+=1
            patient_vault[normalized_value] = f"{entity_type}_ID_{vault_counter}>"

        token = patient_vault[normalized_value]
        anonymized_text = anonymized_text[:result.start] + token + anonymized_text[result.end:]

    print(anonymized_text)

    print(json.dumps(patient_vault, indent=4))

if __name__== "__main__":
    anonymize_vault()
