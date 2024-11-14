import json
import cohere
from enum import Enum
from pathlib import Path
import sys

# API key is loaded from environment variables
co = cohere.ClientV2(api_key=None, log_warning_experimental_features=False)

class TextType(str, Enum):
    article = "Article"


# Dictionary for text type prompts
text_type_prompts = {
    TextType.article: [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "Huisstijlgids:\n```" + Path('api/data/rules/huisstijlgids 1-4.txt').read_text() + "\n```\n" + """
Generate a JSON giving list of corrections made to the text, including bad words, suggestions, and explanations. With fields "rule_reference", "incorrect_part", "corrected_part", "explanation", "severity".

"rule_reference": The specific rule from the huisstijlgids that applies to this error. In the format 'X.Y Name'
"incorrect_part": The part of the text that contains the error, marked for replacement.
"corrected_part": The suggested correct version of the incorrect part.
"explanation": A brief explanation in Dutch regarding the error and suggestion from the Huisstijlgids in context.
"error_severity": The severity of the rule broken from 0.0 to 1.0. How badly is the rule being broken.
"start_index": The starting character index of the incorrect part within the full text.
"end_index": The ending character index of the incorrect part within the full text."""
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
    ]
}

# Function to process text and call Cohere API


def get_suggestions(text: str, text_type: TextType):
    if not isinstance(text_type, TextType):
        return "Invalid text type"

    messages = text_type_prompts[text_type]

    messages.append({"role": "user", "content": f"```{text}```"})

    print("Calling API")
    response = co.chat(model="command-r-plus-08-2024",
                       messages=messages,
                       temperature=0.7,
                       response_format={
                           "type": "json_object",
                           "schema": {
                               "type": "object",
                               "properties": {
                                   "corrections": {
                                       "type": "array",
                                       "items": {
                                           "type": "object",
                                           "properties": {
                                               "rule_reference": {
                                                   "type": "string"
                                               },
                                               "incorrect_part": {
                                                   "type": "string"
                                               },
                                               "corrected_part": {
                                                   "type": "string"
                                               },
                                               "explanation": {
                                                   "type": "string"
                                               },
                                               "error_severity": {
                                                   "type": "number"
                                               },
                                               "start_index": {
                                                   "type": "integer"
                                               },
                                               "end_index": {
                                                   "type": "integer"
                                               }
                                           },
                                           "required": [
                                               "rule_reference",
                                               "incorrect_part",
                                               "corrected_part",
                                               "explanation",
                                               "error_severity",
                                               "start_index",
                                               "end_index"
                                           ]
                                       }
                                   }
                               },
                               "required": [
                                   "corrections"
                               ]
                           }
                       })
    print("Got response!")

    # Possible to use extra return values to determine accuracy

    return response.message.content[0].text.strip()


if __name__ == '__main__':
    number = (sys.argv[1] if len(sys.argv) > 1 else 1)

    input = Path(f'api/data/input/{number}.txt').read_text(encoding='utf-8')
    output = get_suggestions(input, TextType.article)
    output = output.removesuffix("```").removeprefix("```")

    json_object = json.loads(output)
    json_formatted_str = json.dumps(json_object, indent=2)

    print(json_formatted_str)
    file = Path(f'data/output/cohere/{number}.json')
    file.write_text(json_formatted_str, encoding='utf-8')
