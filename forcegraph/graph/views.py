import json
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from ptal_api.providers.gql_providers import KeycloakAwareGQLClient
from .models import Stands
from graphql import GraphQLError

realm = "core"
client_id = "web-ui"
client_key = "039f8182-db0a-45d9-bc25-e1a979b06bfd"

def auth_view(request):
    stands = Stands.objects.all()

    if request.method == "POST":
        stand_name = request.POST.get("stand")
        username = request.POST.get("login")
        password = request.POST.get("password")
        research_map = request.POST.get("research_map")

        try:
            stand = Stands.objects.get(stand=stand_name)
            stand_url = stand.stand_url
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
                    paginationConcept(extraSettings: {{ searchOnMap: true }}) {{
                      listConcept {{
                        id
                        name
                        image {{
                            thumbnail
                        }}
                        conceptType {{
                          id
                          name
                        }}
                        paginationConceptProperty(filterSettings: {{ status: approved }}) {{
                          listConceptProperty {{
                            propertyType {{
                              id
                              name
                            }}
                            value {{
                              __typename
                              ... on CompositeValue {{
                                listValue {{
                                  propertyValueType {{
                                    id
                                  }}
                                  value {{
                                    __typename
                                    ... on DateTimeValue {{
                                      date {{
                                        day
                                        month
                                        year
                                      }}
                                      time {{
                                        hour
                                        minute
                                        second
                                      }}
                                    }}
                                    ... on DoubleValue {{
                                      floatValue: value
                                    }}
                                    ... on GeoPointValue {{
                                      name
                                      point {{
                                        latitude
                                        longitude
                                      }}
                                    }}
                                    ... on IntValue {{
                                      intValue: value
                                    }}
                                    ... on LinkValue {{
                                      linkValue: link
                                    }}
                                    ... on StringLocaleValue {{
                                      stringLocaleValue: value
                                      locale
                                    }}
                                    ... on StringValue {{
                                      stringValue: value
                                    }}
                                    ... on TimestampValue {{
                                      timestampValue: value
                                    }}
                                  }}
                                }}
                              }}
                              ... on DateTimeValue {{
                                date {{
                                  day
                                  month
                                  year
                                }}
                                time {{
                                  hour
                                  minute
                                  second
                                }}
                              }}
                              ... on DoubleValue {{
                                floatValue: value
                              }}
                              ... on GeoPointValue {{
                                name
                                point {{
                                  latitude
                                  longitude
                                }}
                              }}
                              ... on IntValue {{
                                intValue: value
                              }}
                              ... on LinkValue {{
                                linkValue: link
                              }}
                              ... on StringLocaleValue {{
                                stringLocaleValue: value
                                locale
                              }}
                              ... on StringValue {{
                                stringValue: value
                              }}
                              ... on TimestampValue {{
                                timestampValue: value
                              }}
                            }}
                          }}
                        }}
                        paginationConceptLink(filterSettings: {{}}) {{
                          listConceptLink {{
                            from {{
                              ... on Concept {{
                                id
                                name
                              }}
                            }}
                            to {{
                              ... on Concept {{
                                id
                                name
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

                # Проверка на специфические сообщения об ошибке
                def find_message(obj, targets):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k == "message" and v in targets:
                                return v
                            result = find_message(v, targets)
                            if result:
                                return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = find_message(item, targets)
                            if result:
                                return result
                    return None

                error_type = find_message(response, {"ResearchMap.NotFound", "ID.UnexpectedError"})
                if error_type:
                    if error_type == "ResearchMap.NotFound":
                        messages.error(request, "Исследовательская карта не найдена.")
                    elif error_type == "ID.UnexpectedError":
                        messages.error(request, "Произошла ошибка при обработке Идентификатора ИК.")
                    return redirect("auth_view")

                return render(request, "3d_graph.html", {"response": json.dumps(response), "stand_url": stand_url})

        except Stands.DoesNotExist:
            messages.error(request, "Указанный стенд не найден.")
            return redirect("auth_view")

        except GraphQLError as e:
            messages.error(request, f"Ошибка GraphQL: {str(e)}")
            return redirect("auth_view")

        except Exception as e:
            error_text = str(e)
            match = re.search(r"\{.*\}", error_text)
            if match:
                try:
                    error_json = json.loads(match.group())
                    if error_json.get("error") == "invalid_grant":
                        messages.error(request, "Неверный логин или пароль.")
                    else:
                        desc = error_json.get("error_description", "неизвестная причина")
                        messages.error(request, f"Ошибка авторизации: {desc}")
                except json.JSONDecodeError:
                    if "401" in error_text:
                        messages.error(request, "Неверный логин или пароль.")
                    elif "403" in error_text:
                        messages.error(request, "Доступ запрещён.")
                    else:
                        messages.error(request, f"Произошла ошибка: {error_text}")
            else:
                if "401" in error_text:
                    messages.error(request, "Неверный логин или пароль.")
                elif "403" in error_text:
                    messages.error(request, "Доступ запрещён.")
                elif "404" in error_text:
                    messages.error(request, "Сервис не найден.")
                elif "500" in error_text:
                    messages.error(request, "Внутренняя ошибка сервера.")
                else:
                    messages.error(request, f"Произошла непредвиденная ошибка: {error_text}")
            return redirect("auth_view")

    return render(request, "auth_form.html", {
        "stands": stands
    })
