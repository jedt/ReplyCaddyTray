import unittest
import os
import sys
import importlib
import chromadb
import ollama

# import app
sys.path.append("../")
from app import app

# def import_path(module_name, path):
#     try:
#         if os.path.exists(path):
#             source_file_loader = importlib.machinery.SourceFileLoader(module_name, path)
#             spec = importlib.util.spec_from_loader(module_name, source_file_loader)
#             module = importlib.util.module_from_spec(spec)
#             sys.modules[module_name] = module
#             spec.loader.exec_module(module)
#
#             return module
#     except TypeError:
#         print("can't import Type error")
#         return None
#     except ModuleNotFoundError:
#         print("can't import")
#         return None


class MyTestCase(unittest.TestCase):
    def test_embedding(self):
        text_embedding = app.get_text_embedding_dim("Hello, world")
        self.assertEqual(text_embedding.shape, (1024,))

    def test_chromadb_collection(self):

        client = chromadb.PersistentClient(path=app.get_local_db_dir_path())

        collection = app.create_chunks_persistent_store_if_not_exists(
            app.get_local_db_dir_path(), "test"
        )

        documents = [
            "Llamas are members of the camelid family meaning they're pretty closely related to vicuñas and camels",
            "Llamas were first domesticated and used as pack animals 4,000 to 5,000 years ago in the Peruvian highlands",
            "Llamas can grow as much as 6 feet tall though the average llama between 5 feet 6 inches and 5 feet 9 inches tall",
            "Llamas weigh between 280 and 450 pounds and can carry 25 to 30 percent of their body weight",
            "Llamas are vegetarians and have very efficient digestive systems",
            "Llamas live to be about 20 years old, though some only live for 15 years and others live to be 30 years old",
        ]

        for i, d in enumerate(documents):
            response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
            embedding = response["embedding"]
            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[d],
            )

        # an example prompt
        prompt = "What animals are llamas related to?"

        # generate an embedding for the prompt and retrieve the most relevant doc
        response = ollama.embeddings(prompt=prompt, model="mxbai-embed-large")
        results = collection.query(
            query_embeddings=[response["embedding"]], n_results=2
        )
        data = results["documents"][0][0]
        print(data)


if __name__ == "__main__":
    unittest.main()
