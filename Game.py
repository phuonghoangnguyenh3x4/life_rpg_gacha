import json
import random

class Game:
    COST_PER_GACHA = 1000

    def __init__(self, notionPy, STORE_DB_ID, PLAYER_DB_ID):
        self.notionPy = notionPy
        self.STORE_DB_ID = STORE_DB_ID
        self.PLAYER_DB_ID = PLAYER_DB_ID
        self.collectables = self.get_collectables()

    def get_player_collection(self, player):
        collection = player['properties']['ColHelper']['formula']['string']
        collection = collection.split('@')[1:]
        collection = self.search_collectables_by_titles(collection)
        return collection

    def get_collectables(self):
        store = self.notionPy.get_database(self.STORE_DB_ID)
        collectables = self.__filter_collectable(store)
        collectables = self.__extract_fields(collectables)
        collectables = self.__assign_probabilities(collectables)
        return collectables
    
    def search_collectables_by_titles(self, titles):
        return [
            collectable for collectable in self.collectables
            if collectable["title"] in titles
        ]

    def get_n_random_collectables(self, n):
        random_collectables = self.__select_random_objects(self.collectables, n)
        return random_collectables

    def buy_collectables(self, player, random_collectables):
        response = self.__update_external_collectables(player, random_collectables)
        if response:
            self.__update_gacha_cost(player, len(random_collectables)*Game.COST_PER_GACHA)
            return True

        return False
    
    def get_players(self):
        return self.notionPy.get_database(self.PLAYER_DB_ID)
        
    def __filter_collectable(self, store):
        collectable_objects = [
            obj for obj in store
            if obj.get("properties", {}).get("Type", {}).get("select", {}).get("name") == "Collectable"
        ]
        return collectable_objects

    def __get_image_url(self, page_id):
        page_content = self.notionPy.get_page_content(page_id)
        return page_content[0]['image']['file']['url']

    # Extract the `id`, `title`, `rarity`, `image_url` and `cost` from Collectables
    def __extract_fields(self, data):
        extracted_data = []
        
        for obj in data:
            # Get properties
            properties = obj.get("properties", {})
            title = properties.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "")
            rarity = properties.get("Rarity", {}).get("select", {}).get("name", "")
            cost = properties.get("Cost", {}).get("formula", {}).get("number", 0)
            obj_id = obj.get("id", "")
            image_url = self.__get_image_url(obj_id)
            
            # Append to result list
            extracted_data.append({
                "id": obj_id,
                "title": title,
                "rarity": rarity,
                "cost": cost,
                "image_url": image_url
            })
        return extracted_data

    def __assign_probabilities(self, data):
        # Define probability mapping for rarities
        rarity_probabilities = {
            "Common": 0.5,       # 50%
            "Rare": 0.25,        # 25%
            "SuperRare": 0.1,    # 10%
            "Epic": 0.07,        # 7%
            "Secret": 0.05,      # 5%
            "Legendary": 0.03    # 3%
        }

        
        for obj in data:
            rarity = obj["rarity"] 
            obj["probability"] = rarity_probabilities[rarity] 
        return data

    def __select_random_objects(self, data, n):
        selected_objects = random.choices(
            population=data,
            weights=[obj['probability'] for obj in data],
            k=n
        )
        return selected_objects
    
    def __get_gacha_cost(self, player):
        return player['properties']['GachaCost']['number']

    def __update_gacha_cost(self, player, cost):
        gacha_cost = self.__get_gacha_cost(player)
        gacha_cost = gacha_cost if gacha_cost else 0
        player_id = self.notionPy.get_page_id(player)
        return self.notionPy.update_property(player_id, "GachaCost", gacha_cost + cost)

    def __get_external_collectables_ids(self, player):
        ids = player['properties']['ExternalCol']['relation']
        return [id['id'] for id in ids]

    def __update_external_collectables(self, player, random_collectables):
        related_page_ids = self.notionPy.get_page_ids(random_collectables)
        relation_property_name = "ExternalCollectables"
        player_id = self.notionPy.get_page_id(player)
        external_collectables_ids = self.__get_external_collectables_ids(player)
        return self.notionPy.link_to_relation(player_id, relation_property_name, external_collectables_ids + related_page_ids)

    
