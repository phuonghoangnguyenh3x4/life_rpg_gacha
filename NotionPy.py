from notion_client import APIResponseError, Client

class NotionPy:
    def __init__(self, NOTION_API_KEY):
        self.notion = Client(auth=NOTION_API_KEY)
        
    def get_database(self, database_id):
        response = self.notion.databases.query(database_id=database_id)
        response = response.get("results", [])
        return response
    
    def link_to_relation(self, page_id, relation_property_name, related_page_ids):
        relation_data = [{"id": related_page_id} for related_page_id in related_page_ids]
        
        try:
            response = self.notion.pages.update(
                page_id=page_id,
                properties={
                    relation_property_name: {"relation": relation_data}
                }
            )
            return response
        
        except APIResponseError as e:
            self.__printAPIResponseError(e)
        
        return None
    
    def update_property(self, page_id, relation_property_name, value):
        try:
            response = self.notion.pages.update(
                page_id=page_id,
                properties={
                    relation_property_name: value
                }
            )
            return response
        
        except APIResponseError as e:
            self.__printAPIResponseError(e)
        
        return None
    
    def __printAPIResponseError(self, e):
        print("Error while updating the page!")
        print(f"Status Code: {e.response.status_code}")
        print(f"Error Message: {e.message}")
        print(f"Error Code: {e.code}")

    def get_page_id(self, page):
        return page['id']

    def get_page_ids(self, pages):
        return [page['id'] for page in pages]
    
    def search_by_title(self, results, title):
        matching_objects = [
            obj for obj in results
            if obj.get("properties", {}).get("Name", {}).get("title", [{}])[0]
            .get("text", {}).get("content") == title
        ]
        return matching_objects
    
    def get_page_content(self, page_id):
        page = self.notion.blocks.children.list(block_id=page_id)
        return page.get("results", [])
