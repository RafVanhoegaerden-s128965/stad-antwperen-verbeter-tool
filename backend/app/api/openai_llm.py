import json
from pprint import pprint
from openai import OpenAI
from enum import Enum
from pathlib import Path
import sys
import os

# Enum for text medium
class TextType(str, Enum):
    article = "Article"


class OpenAILLM:
    def __init__(self, api_key: str | None):
        self.client = OpenAI(
          organization='org-XmfHwuYPEnDEdDdQUrpNxS2d',
          api_key=api_key
        )
        self.prompt_dict = {}
        self.load_prompts()
    
    def load_prompts(self):
        dir = os.path.abspath(os.path.dirname(__file__))
        rules_path = os.path.join(dir, 'data/rules/huisstijlgids 1-4.txt')
        self.prompt_dict = {
          TextType.article: [
          {
            "role": "system",
            "content": [
              {
                "type": "text",
                "text": "Huisstijlgids:\n```" + Path(rules_path).read_text() + "\n```"
              }
            ]
          },
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": "WIN!!! EEN DUOVIPTICKET VOOR Antwerp Giants vs. Fribourg Olympic OP 23/10 \nGisteren, 13u \n \nOp woensdag, 23 oktober zullen Antwerp Giants in de FIBA Europe Cup proberen om een tweede overwinning te halen in Lotto Arena. De tegenstander zal het Zwitserse Fribourg Olympic zijn. Doe mee met onze wedstrijd en win 1 van de 5 exclusieve VIPtickets. \n \nAntwerp Giants is 1 van de 3 Belgische teams in de FIBA Europe Cup. Ze spelen in de poulefase tegen het Franse Cholet, het Roemeense Constanta en het Zwitserse Fribourg Olympic. Na een grote overwinning in Roemenië, werd de eerste thuismatch in de Lotto Arena verloren tegen Cholet. Op woensdag, 23 oktober, proberen de Giants hun tweede Europese overwinning binnen te halen tegen Fribourg Olympic. \n \nDoe mee en WIN!!! een van de drie duoviptickets \n- Vul het formulier in via de wedstrijdpagina. \n- Je kunt meedoen tot zondag 20/10 om 23:59. \n- We contacteren op maandag 21 oktober de vijf winnende personen. Zij krijgen hun tickets opgestuurd via email. \n \nInfo \nFIBA Europe Cup | Antwerp Giants vs. Fribourg Olympic (ZWI) \nwoensdag 23/10 om 20u \nLotto Arena, Schijnpoortweg 119, 2170 Merksem \n"
              }
            ]
          },
          {
            "role": "assistant",
            "content": [
              {
                "type": "text",
                "text": "{\"corrections\":[{\"rule_reference\":\"1.2 Flamboyant\",\"incorrect_part\":\"WIN!!! EEN DUOVIPTICKET VOOR\",\"corrected_part\":\"Win een duovipticket voor\",\"explanation\":\"Vermijd het gebruik van hoofdletters en meerdere uitroeptekens om te voorkomen dat de tekst schreeuwerig overkomt. Dit kan de lezer afschrikken.\",\"error_severity\":0.8},{\"rule_reference\":\"4.11 Niet te enthousiast\",\"incorrect_part\":\"Doe mee en WIN!!! een van de drie duoviptickets\",\"corrected_part\":\"Doe mee en win een van de drie duoviptickets\",\"explanation\":\"Het gebruik van hoofdletters en meerdere uitroeptekens kan de lezer afschrikken en komt overdreven enthousiast over. Houd de toon informatief en laat de lezer zelf bepalen of iets spannend is.\",\"error_severity\":0.7},{\"rule_reference\":\"4.9 Gebruik niet te veel letterwoorden en afkortingen\",\"incorrect_part\":\"VIPtickets\",\"corrected_part\":\"VIP-tickets\",\"explanation\":\"Gebruik koppeltekens om de leesbaarheid van samengestelde woorden te verbeteren.\",\"error_severity\":0.3},{\"rule_reference\":\"4.2 Vermijd ambtelijke, moeilijke of lange woorden\",\"incorrect_part\":\"exclusieve VIPtickets\",\"corrected_part\":\"exclusieve VIP-tickets\",\"explanation\":\"Zorg voor een duidelijke structuur in samengestelde woorden zoals 'VIP-tickets' door een koppelteken te gebruiken.\",\"error_severity\":0.3},{\"rule_reference\":\"4.8 Vermijd vage woorden\",\"incorrect_part\":\"Gisteren, 13u\",\"corrected_part\":\"Donderdag om 13:00\",\"explanation\":\"Gebruik specifieke tijdsaanduidingen om verwarring te voorkomen, vooral als de tekst later wordt gelezen.\",\"error_severity\":0.5},{\"rule_reference\":\"4.8 Vermijd vage woorden\",\"incorrect_part\":\"tot zondag 20/10 om 23:59\",\"corrected_part\":\"tot zondag 20 oktober om 23:59\",\"explanation\":\"Gebruik volledige datums en tijden om duidelijkheid te verschaffen.\",\"error_severity\":0.5},{\"rule_reference\":\"4.8 Vermijd vage woorden\",\"incorrect_part\":\"woensdag 23/10 om 20u\",\"corrected_part\":\"woensdag 23 oktober om 20:00\",\"explanation\":\"Gebruik volledige datums en tijden om duidelijkheid te verschaffen.\",\"error_severity\":0.5},{\"rule_reference\":\"4.5 Schrijf actief\",\"incorrect_part\":\"werden de eerste thuismatch in de Lotto Arena verloren tegen Cholet\",\"corrected_part\":\"verloren de Giants de eerste thuismatch in de Lotto Arena tegen Cholet\",\"explanation\":\"Actief schrijven maakt de tekst levendiger en directer, waardoor de lezer beter begrijpt wie de actie onderneemt.\",\"error_severity\":0.6}]}"
              }
            ]
          }
        ],
      }

    # Function to process text and call Cohere API
    def get_suggestions_stream(self, text: str, text_type: TextType):
        if not any(text_type == item.value for item in TextType):
            return "Invalid text type"
        
        messages = self.prompt_dict[text_type]

        messages.append({"role": "user", "content": f"{text}"})
        
        print("Calling API")
        
        response_text = ""
        with self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.65,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                "name": "text_correction_schema",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                    "corrections": {
                        "type": "array",
                        "description": "A list of corrections made to the text, including bad words, suggestions, and explanations.",
                        "items": {
                        "type": "object",
                        "properties": {
                            "rule_reference": {
                            "type": "string",
                            "description": "The specific rule from the huisstijlgids that applies to this error. In the format 'X.Y Name'"
                            },
                            "incorrect_part": {
                            "type": "string",
                            "description": "The part of the text that contains the error, marked for replacement."
                            },
                            "corrected_part": {
                            "type": "string",
                            "description": "The suggested correct version of the incorrect part."
                            },
                            "explanation": {
                            "type": "string",
                            "description": "A brief explanation in Dutch regarding the error and suggestion from the Huisstijlgids in context."
                            },
                            "error_severity": {
                            "type": "number",
                            "description": "The severity of the rule broken from 0.0 to 1.0. How badly is the rule being broken."
                            }
                        },
                        "required": [
                            "rule_reference",
                            "incorrect_part",
                            "corrected_part",
                            "explanation",
                            "error_severity"
                        ],
                        "additionalProperties": False
                        }
                    }
                    },
                    "required": [
                    "corrections"
                    ],
                    "additionalProperties": False
                }
                }
            },
            stream=True
        ) as stream:
            for chunk in stream:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    # Accumulate the content only if it's not None
                    response_text += chunk.choices[0].delta.content
                    yield f"{chunk.choices[0].delta.content}"
                if chunk.choices[0].finish_reason == "stop":
                    break  # Stop if the finish reason is 'stop'
        
        print("Got response!")
        
        return response_text

    def get_suggestions(self, text: str, text_type: TextType):
        if not any(text_type == item.value for item in TextType):
            return {"error": "Invalid text type"}
        
        output = ""
        for content in self.get_suggestions_stream(text, text_type):
            output += content
        output = output.removesuffix("```").removeprefix("```")

        json_object = json.loads(output)
        json_formatted_str = json.dumps(json_object, indent=2)
        
        return json_formatted_str.strip()

    
if __name__ == '__main__':
    number = (sys.argv[1] if len(sys.argv) > 1 else 1)
    
    client = OpenAILLM()

    input = Path(f'data/input/{number}.txt').read_text(encoding='utf-8')
    output = ""
    for content in client.get_suggestions_stream(input, TextType.article):
        output += content
    output = output.removesuffix("```").removeprefix("```")

    json_object = json.loads(output)
    json_formatted_str = json.dumps(json_object, indent=2)

    print(json_formatted_str)
    Path(f'data/output/openai/{number}.json').write_text(json_formatted_str, encoding='utf-8')