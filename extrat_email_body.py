import json
import base64
import re
from bs4 import BeautifulSoup # used for finding/replacing URLs, email addresses, and special characters
import random
import string

with open('messages.jsonl', 'r') as input_file:
    with open('output.jsonl', 'w') as output_file:
        last_prompt = None
        last_completion = None
        for line in input_file:
            item = json.loads(line)
            if 'data' in item['payload']['body']:
                data = item['payload']['body']['data']
            else:
                data = ''
            #Find decodable base64 lines in data. Theses are the message contents.
            try:
                decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
            except (TypeError, ValueError):
                decoded_data = ''
            if decoded_data:
                soup = BeautifulSoup(decoded_data, 'html.parser')

                # Replace hyperlinked text with the link itself rather than just the text, e.g. https://website.com instead of "Click here."
                for link in soup.find_all('a'):
                    link_text = link.text.strip()
                    link_url = link.get('href')
                    if link_url is not None:
                        link.replace_with(link_url + ' ')

                # Replace formatting characters with blank space.
                plain_text = soup.get_text().replace('\r', ' ').replace('\n', ' ').replace('->', '')

                # Anonymize all email addresses that appear in communications.
                def random_email(match):
                    letters = string.ascii_letters + string.digits
                    return ''.join(random.choice(letters) for i in range(10)) + '@' + ''.join(random.choice(letters) for i in range(5)) + '.' + ''.join(random.choice(string.ascii_lowercase) for i in range(3))

                plain_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', random_email, plain_text)

                # Find prompts, i.e. questions sent from users to support inbox
                prompt_pattern = r'> wrote:\s*(.*?)\s*> wrote:'

                matches = re.findall(prompt_pattern, plain_text, re.DOTALL)

                if len(matches) > 0:
                    prompt = matches[0].strip()
                else:
                    prompt = plain_text.split('> wrote:')[-1].strip()
                prompt = prompt.split('\t')[0].strip()

                # Find completions, i.e. our answer to the user in response to their question
                completion_end = plain_text.find('--')
                completion = plain_text[:completion_end].strip()

                prompt = prompt.replace('mailto:', '')
                completion = completion.replace('mailto:', '')

                if prompt and completion:
                    output_item = {'prompt':prompt + ' ->','completion':completion + '\n'}
                    output_line = json.dumps(output_item)
                    output_file.write(output_line + '\n')
