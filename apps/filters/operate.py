class FilterFields:
    
    FIELDS = [
                'mission_type',
                'created_after',
                'category_list',
                'name_contains',
                'description_contains',
                'status_list',
                'location_list',]

    def on_create():
        return FilterFields.FIELDS
    def on_get():
        return FilterFields.FIELDS
    def on_update():
        return FilterFields.FIELDS
    def on_delete():
        return ['owner']