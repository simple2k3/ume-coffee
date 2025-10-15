from first_app.models import Categories
class CategoriesServices:
    @staticmethod
    def get_all_categories():
        categories = Categories.objects.all()
        result = []
        for category in categories:
            result.append({
                "categories_id": category.categories_id,
                "categories_name": category.categories_name
            })
        return result
