import json
from django.shortcuts import render
from ptal_api.providers.gql_providers import KeycloakAwareGQLClient
from .models import Stands
from requests.exceptions import HTTPError
from graphql import GraphQLError

realm = "core"
client_id = "web-ui"
client_key = "039f8182-db0a-45d9-bc25-e1a979b06bfd"

def auth_view(request):
    stands = Stands.objects.all()
    error_message = None

    if request.method == "POST":
        stand_name = request.POST.get("stand")
        username = request.POST.get("login")
        password = request.POST.get("password")
        research_map = request.POST.get("research_map")

        try:
            stand = Stands.objects.get(stand=stand_name)
            graphql_url = stand.graphql_url
            keycloak_auth_url = stand.auth_url

            with KeycloakAwareGQLClient(
                graphql_url, 10000, 5,
                auth_url=keycloak_auth_url,
                realm=realm, client_id=client_id,
                user=username, pwd=password,
                client_secret=client_key
            ) as gql_client:

                query = f"""
                query MyQuery {{
                  researchMap(id: "{research_map}") {{
                    id
                    name
                    paginationConcept(extraSettings: {{searchOnMap: true}}) {{
                      listConcept {{
                        id
                        name
                        conceptType {{
                          id
                          name
                        }}
                        paginationConceptLink(filterSettings: {{}}) {{
                          listConceptLink {{
                            from {{
                              ... on Concept {{
                                id
                                name
                                conceptType {{
                                  name
                                  id
                                }}
                              }}
                            }}
                            to {{
                              ... on Concept {{
                                id
                                name
                                conceptType {{
                                  name
                                  id
                                }}
                              }}
                            }}
                            conceptLinkType {{
                              id
                              name
                            }}
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

                return render(request, "3d_graph.html", {"response": json.dumps(response)})

        except Stands.DoesNotExist:
            error_message = "Указанный стенд не найден."
        except HTTPError as e:
            error_message = f"Ошибка авторизации: {e.response.status_code} - {e.response.reason}"
        except GraphQLError as e:
            error_message = f"Ошибка GraphQL: {str(e)}"
        except Exception as e:
            error_message = f"Произошла непредвиденная ошибка: {str(e)}"

    return render(request, "auth_form.html", {
        "stands": stands,
        "error": error_message
    })
