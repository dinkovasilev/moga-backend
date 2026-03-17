from django.db import models

class TCategory(models.Model):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey(
        "self",
        related_name="subcategories",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    def __str__(self) -> str:
        return self.name
    @classmethod
    def link(cls, category:str|object, subcategory:str):
        try:
            if not isinstance(category,TCategory):
                category = cls.objects.get(name=category)
            cls.objects.get_or_create(name=subcategory,parent=category)
            return True
        except: return False



class ICategory(models.Model):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey(
        "self",
        related_name="subcategories",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    def __str__(self) -> str:
        return self.name

