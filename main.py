import json
from ptal_api.adapter import TalismanAPIAdapter
from ptal_api.providers.gql_providers import KeycloakAwareGQLClient
from ptal_api.schema.api_schema import ConceptFilterSettings, LinkFilterSettings, PropertyFilterSettings, ConceptMutationInput

graphql_uri = 'https://mgimo.talisman.ispras.ru/graphql'
keykloak_auth_url = 'https://mgimo.talisman.ispras.ru/auth/'
realm = 'core'
cliend_id = 'web-ui'
client_key = '039f8182-db0a-45d9-bc25-e1a979b06bfd'
# Указать свои данные для доступа к стенду
user = 'gikostandi'
pwd = 'f7htXAMP'

gql_client = KeycloakAwareGQLClient(
    graphql_uri, 10000, 5,
    auth_url=keykloak_auth_url,
    realm=realm, client_id=cliend_id, user=user, pwd=pwd,
    client_secret=client_key
).__enter__()

print(gql_client)

# Ваш GraphQL-запрос
query = """
query MyQuery {
  researchMap(id: "347") {
    id
    name
    paginationConcept(extraSettings: {searchOnMap: true}) {
      listConcept {
        id
        name
        paginationConceptLink(filterSettings: {}) {
          listConceptLink {
            id
            conceptFromId
            conceptToId
          }
        }
      }
    }
  }
}
"""
# 🔹 Выполнение запроса
response = gql_client.execute(query)

# 🔹 Вывод результата
print(response)

# 🔹 Запись JSON в файл
with open("response.json", "w", encoding="utf-8") as file:
    json.dump(response, file, indent=4, ensure_ascii=False)

print("✅ Ответ записан в response.json")