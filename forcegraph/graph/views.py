
import json
from django.shortcuts import render
from ptal_api.providers.gql_providers import KeycloakAwareGQLClient

#cтенды (в будушем сделать через БД)
STANDS = {
    "MGIMO": {
        "graphql_uri": "https://mgimo.tыalisman.ispras.ru/graphql",
        "auth_url": "https://mgimo.talisman.ispras.ru/auth/",
    }
}

realm = "core"
client_id = "web-ui"
client_key = "039f8182-db0a-45d9-bc25-e1a979b06bfd"

def auth_view(request):
    if request.method == "POST":
        stand_id = request.POST.get("stand")
        username = request.POST.get("login")
        password = request.POST.get("password")
        research_map = request.POST.get("research_map")

        if stand_id not in STANDS:
            return render(request, "auth_form.html", {"error": "Выбран некорректный стенд"})

        graphql_uri = STANDS[stand_id]["graphql_uri"]
        keycloak_auth_url = STANDS[stand_id]["auth_url"]

        # Создаем GraphQL-клиент
        gql_client = KeycloakAwareGQLClient(
            graphql_uri, 10000, 5,
            auth_url=keycloak_auth_url,
            realm=realm, client_id=client_id, user=username, pwd=password,
            client_secret=client_key
        ).__enter__()

        query = f"""
        query MyQuery {{
          researchMap(id: "{research_map}") {{
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


        return render(request, "result.html", {"response": response})

    return render(request, "auth_form.html")
