from typing import List

import strawberry
from strawberry.scalars import JSON
from src.cache import cache
import json

# TODO: Use JSON strawberry scalars instead to avoic having to (de)serialize explicitly?

@strawberry.input(description="The search query.")
class SearchQuery:
    input: str


@strawberry.interface
class Item:
    name: str
    id: str  # strawberry.ID


@strawberry.type
class IngredientMetadata(Item):
    price: float
    url: str
    alcoholic: bool


@strawberry.type
class Ingredient(Item):
    metadata: IngredientMetadata


@strawberry.type
class Recipe(Item):
    ingredients: List[Ingredient | None]
    instructions: str


def search_placeholder(ingredient_id: str) -> IngredientMetadata | None:
    match ingredient_id:
        case "absolutvodka":
            result = IngredientMetadata(
                name="Absolut Vodka",
                id=ingredient_id,
                price=100.0,
                url="google.se",
                alcoholic=True,
            )
        case "gin":
            result = IngredientMetadata(
                name="Gin",
                id=ingredient_id,
                price=70.0,
                url="google.se",
                alcoholic=True,
            )
        case "tonic":
            result = IngredientMetadata(
                name="Tonic",
                id=ingredient_id,
                price=10.0,
                url="ica.se",
                alcoholic=False,
            )
        case _:
            # TODO: what is best practice of handling errors here?
            print(f"Ingredient_id {ingredient_id} not found!")
            return None

    return result


# Mock data
def _get_ingredient_metadata(ingredient_id: str) -> IngredientMetadata:
    cached_value = cache.get(key=ingredient_id, client=redis_client)
    if cached_value is None:
        print(f"Ingredient ID {ingredient_id} not in cache, searching db.")
        result = search_placeholder(ingredient_id=ingredient_id)
        cache.set(key=ingredient_id, value=json.dumps(result.__dict__), client=redis_client)
    else:
        print(f"Ingredient ID {ingredient_id} served from cache.")
        result_dict = json.loads(cached_value)
        result = IngredientMetadata( # TODO: deserialize more elegantly
            name=result_dict['name'],
            id=result_dict['id'],
            price=result_dict['price'],
            url=result_dict['url'],
            alcoholic=result_dict['alcoholic'],
        )
    return result


def _get_ingredient(recipe_id: str) -> List[Ingredient | None]:
    result = []
    match recipe_id:
        case "justvodka":
            result.append(
                Ingredient(
                    name="Absolut Vodka",
                    id=recipe_id,
                    metadata=_get_ingredient_metadata(
                        "absolutvodka"
                    ),
                )
            )
        case "gintonic":
            result.append(
                Ingredient(
                    name="Gin",
                    id="gin",
                    metadata=_get_ingredient_metadata("gin"),
                )
            )
            result.append(
                Ingredient(
                    name="Tonic",
                    id="tonic",
                    metadata=_get_ingredient_metadata("tonic"),
                )
            )
        case _:
            result.append(None)
    return result


def _get_recipe(query: str) -> List[Recipe | None]:
    match query:
        case "vodka":
            result = Recipe(
                name="Just Vodka",
                id="justvodka",
                ingredients=_get_ingredient("justvodka"),
                instructions="Drink it.",
            )
        case "gin":
            result = Recipe(
                name="Gin & Tonic",
                id="gintonic",
                ingredients=_get_ingredient("gintonic"),
                instructions="Mix and drick.",
            )
        case _:
            result = None
    return [result]


@strawberry.type
class RecipeResultPage:
    search_query: int
    result_items: List[Recipe]


@strawberry.type
class IngredientResultPage:
    search_query: int
    result_items: List[Ingredient]


@strawberry.type
class Query:
    @strawberry.field
    def get_recipes(self, query: SearchQuery) -> List[Recipe | None]:
        return _get_recipe(query=query.input)

    @strawberry.field
    def get_ingredients(self, query: SearchQuery) -> List[Ingredient | None]:
        return _get_ingredient(recipe_id=query.input)

    @strawberry.field
    def get_ingredient_metadata(self, query: SearchQuery) -> IngredientMetadata | None:
        return _get_ingredient_metadata(ingredient_id=query.input)


# Create schema
schema = strawberry.Schema(query=Query, types=[Recipe, Ingredient, IngredientMetadata])

redis_client = cache.start_redis_client(host='localhost', port=6379)  # TODO: obtain parameters from yaml config
# TODO: write some tests here
