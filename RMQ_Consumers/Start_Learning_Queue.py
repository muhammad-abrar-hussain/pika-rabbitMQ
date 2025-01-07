import os
import sys
import json


# Add the 'packages' folder to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'packages'))

import pika
from database import db_fetch_files, db_save_topics
from openai_api import open_api_get_topics
from extracFileText import extract_text

RABBITMQ_HOST = 'localhost'
START_LEARNING_QUEUE = 'start_learning_queue'


def prepare_content(files):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(base_dir, "assets", "CONSTITTIONAL-HISTORY.pdf")

    extracted_texts = []

    for file_info in files:
        file_path = file_info.get('filepath')
        if file_path:
            try:
                text = extract_text(test_file_path)
                extracted_texts.append(text)
            except Exception as e:
                print(f"Error extracting text from {test_file_path}: {e}")
        else:
            print("File path not found in file info.")
    return "".join(extracted_texts)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=START_LEARNING_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        presentation_id = body.decode()
        files = db_fetch_files(presentation_id)
        if "error" in files:
            print(files["error"])
            return

        files_content = prepare_content(files)

        # topics_response = open_api_get_topics(files_content)
        # print(topics_response)

        topics_response = [{'result': '[\n    {\n        "title": "Constitutional History of Pakistan (1947-1973)",\n        "summary": "Pakistan, after gaining its independence in 1947, has faced a tumultuous constitutional history. It has undergone multiple periods of constitutional crises, martial laws and transitions of power between military and civilian rule. The first constitutional crisis occurred in 1954 when the Governor General dismissed the Constituent Assembly, and the country\'s first constitution was adopted only in 1956. However, it lasted a mere two years before President Iskander Mirza imposed martial law. The Supreme Court validated this and subsequent extra-constitutional actions, invoking the Kelsenian theory in the case of State v. Dosso."\n    },\n    {\n        "title": "Rule of General Ayub Khan and Subsequent Political Developments",\n        "summary": "General Ayub Khan, who was appointed as the Chief Martial Law Administrator, ruled until 1969 after another Constitution was passed in 1962. However, following widespread protests, power was transferred to General Yahya Khan. Under his rule, a disastrous military campaign took place in East Pakistan followed by a military defeat to India in 1971, which led to the creation of Bangladesh. Afterwards, martial law was lifted and a new Constitution was once again promulgated."\n    },\n    {\n        "title": "Establishment of the 1973 Constitution",\n        "summary": "The country experienced another constitutional crisis in 1969 which resulted in the reinstatement of martial law and the abrogation of the Constitution. Following the political tumult and war with India, power was transferred to Zulfiqar Ali Bhutto. It was during his presidency that Pakistan adopted its current Constitution in 1973, which was agreed upon by a consensus of all political parties."\n    }\n]', 'id': 'chatcmpl-Amk4KOev7MoOGSN8EMDAYqz929r5L'}, {'result': '[\n  {\n    "title": "Parliamentary Government in the Constitution of Pakistan",\n    "summary": "The Constitution of Pakistan outlines a parliamentary form of government, following the British model, with the Prime Minister holding executive power and the President operating as a figurehead. It also supports federalism, each of Pakistan\'s four provinces has their own provincial legislatures. The National Assembly is allocated seats based on population demographics, while in Senate all provinces have equal representation."\n  },\n  {\n    "title": "Constitutional Amendments and Judiciary Power",\n    "summary": "Constitutional amendments necessitate two-thirds majority approval in both the National Assembly and Senate. The superior courts, including the Supreme Court and High Courts of each province, hold the authority for judicial reviews of legislation and executive actions for enforcement of Fundamental Rights. These courts also provide safeguards for several rights, though these are subject to the law and can be rather weak."\n  },\n  {\n    "title": "Bill of Rights in the Constitution of Pakistan",\n    "summary": "The 1973 Constitution in Pakistan includes a Bill of Rights. Several rights provisions, such as the freedoms of expression and the prohibition against discrimination, are absolute, while others like deprivation of life or liberty are subject to law \'in the interest of public order or national security\'. Preventive detention is allowed with certain conditions, subject to the approval of a Review Board."\n  },\n  {\n    "title": "Constitutional Shifts during the Zia Era",\n    "summary": "In 1977, the Army took control after allegations of election rigging and the declaration of a nationwide street agitation. The Constitution of Pakistan was not fully abrogated but declared to be held \'in abeyance\'. However, the Supreme Court validated these actions. Changes were made to the Constitution to enhance the President\'s powers, including the capacity to dismiss Parliament, prompting concerns about the independence of judiciary."\n  }\n]', 'id': 'chatcmpl-Amk4qQzej0s1vZzXCcr2ECmTYe7z9'}]
        for group in topics_response:
            try:
                topics = json.loads(group["result"])
                request_completion_id = group["id"]
                for topic in topics:
                    topic_data = {
                        "title": topic["title"],
                        "summary": topic["summary"],
                        "request_completion_id": request_completion_id,
                    }
                    save_result = db_save_topics(topic_data, presentation_id)
                    if "error" in save_result:
                        print(f"Error saving topic: {save_result['error']}")
                    else:
                        print(f"Topic saved: {topic_data['title']}")
            except Exception as e:
                print(f"Error processing group: {str(e)}")

    channel.basic_consume(queue=START_LEARNING_QUEUE, on_message_callback=callback)

    print(' [*] Waiting for messages...')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
