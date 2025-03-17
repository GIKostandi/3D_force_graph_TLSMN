import os, json
from dotenv import load_dotenv
from ptal_api.adapter import TalismanAPIAdapter
from ptal_api.providers.gql_providers import KeycloakAwareGQLClient
from ptal_api.schema.api_schema import ConceptFilterSettings, LinkFilterSettings, PropertyFilterSettings, ConceptMutationInput

graphql_uri = 'https://mgimo.talisman.ispras.ru/graphql'
keycloak_auth_url = 'https://mgimo.talisman.ispras.ru/auth/'
realm = 'core'
client_id = 'web-ui'
client_key = '039f8182-db0a-45d9-bc25-e1a979b06bfd'
load_dotenv()
# Данные для доступа к стенду
user = os.getenv("GQL_USER")
pwd = os.getenv("GQL_PASSWORD")

gql_client = KeycloakAwareGQLClient(
    graphql_uri, 10000, 5,
    auth_url=keycloak_auth_url,
    realm=realm, client_id=client_id, user=user, pwd=pwd,
    client_secret=client_key
).__enter__()

map_id = input("map_id: ")

query = f"""
query MyQuery {{
  researchMap(id: "{map_id}") {{
    id
    name
    paginationConcept(extraSettings: {{searchOnMap: true}}) {{
      listConcept {{
        id
        name
        paginationConceptLink(filterSettings: {{}}) {{
          listConceptLink {{
            id
            conceptFromId
            conceptToId
          }}
        }}
      }}
    }}
  }}
}}
"""
response = gql_client.execute(query)

with open("response.json", "w", encoding="utf-8") as file:
    json.dump(response, file, indent=4, ensure_ascii=False)

print(response)