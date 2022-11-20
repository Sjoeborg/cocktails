from typing import List

import strawberry


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


# Mock data
def _get_ingredient_metadata(ingredient_id: SearchQuery) -> IngredientMetadata:
    match ingredient_id.input:
        case "absolutvodka":
            result = IngredientMetadata(
                name="Absolut Vodka",
                id=ingredient_id.input,
                price=100.0,
                url="google.se",
                alcoholic=True,
            )
        case "gin":
            result = IngredientMetadata(
                name="Gin",
                id=ingredient_id.input,
                price=70.0,
                url="google.se",
                alcoholic=True,
            )
        case "tonic":
            result = IngredientMetadata(
                name="Tonic",
                id=ingredient_id.input,
                price=10.0,
                url="ica.se",
                alcoholic=False,
            )
        case _:
            raise ValueError(f"Ingredient_id {ingredient_id} not found!")
    return result


def _get_ingredient(recipe_id: SearchQuery) -> List[Ingredient | None]:
    result = []
    match recipe_id.input:
        case "justvodka":
            result.append(
                Ingredient(
                    name="Absolut Vodka",
                    id=recipe_id.input,
                    metadata=_get_ingredient_metadata(
                        SearchQuery(input="absolutvodka")
                    ),
                )
            )
        case "gintonic":
            result.append(
                Ingredient(
                    name="Gin",
                    id="gin",
                    metadata=_get_ingredient_metadata(SearchQuery(input="gin")),
                )
            )
            result.append(
                Ingredient(
                    name="Tonic",
                    id="tonic",
                    metadata=_get_ingredient_metadata(SearchQuery(input="tonic")),
                )
            )
        case _:
            result.append(None)
    return result


def _get_recipe(query: SearchQuery) -> List[Recipe | None]:
    match query.input:
        case "vodka":
            result = Recipe(
                name="Just Vodka",
                id="justvodka",
                ingredients=_get_ingredient(SearchQuery(input="justvodka")),
                instructions="Drink it.",
            )
        case "gin":
            result = Recipe(
                name="Gin & Tonic",
                id="gintonic",
                ingredients=_get_ingredient(SearchQuery(input="gintonic")),
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
        return _get_recipe(query=query)

    @strawberry.field
    def get_ingredients(self, query: SearchQuery) -> List[Ingredient | None]:
        return _get_ingredient(recipe_id=query)

    @strawberry.field
    def get_ingredient_metadata(self, query: SearchQuery) -> IngredientMetadata:
        return _get_ingredient_metadata(ingredient_id=query)


# Create schema
schema = strawberry.Schema(query=Query, types=[Recipe, Ingredient, IngredientMetadata])
