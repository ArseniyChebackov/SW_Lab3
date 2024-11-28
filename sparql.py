from SPARQLWrapper import SPARQLWrapper, JSON
from html import unescape

def get_universities_in_ukraine():
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbr: <http://dbpedia.org/resource/>

    SELECT ?university ?name ?type (SAMPLE(?location) AS ?location) (SAMPLE(?website) AS ?website)
    WHERE {
      ?university a ?type ;
                  dbo:country dbr:Ukraine ;
                  rdfs:label ?name .
      OPTIONAL { ?university dbo:location ?location . }
      OPTIONAL { ?university dbo:wikiPageExternalLink ?website . }
      FILTER (lang(?name) = "en")
      VALUES ?type { dbo:University dbo:College dbo:School dbo:FormerHighschool }
    }
    GROUP BY ?university ?name ?type
    LIMIT 200
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    type_mapping = {
        'http://dbpedia.org/ontology/University': 'University',
        'http://dbpedia.org/ontology/College': 'College',
        'http://dbpedia.org/ontology/School': 'School',
        'http://dbpedia.org/ontology/FormerHighschool': 'Former Highschool'
    }

    universities = []
    for result in results["results"]["bindings"]:
        university = {
            "name": unescape(result["name"]["value"]) if "name" in result else "",
            "type": type_mapping.get(result["type"]["value"], "Unknown"),
            "location": result["location"]["value"] if "location" in result else "",
            "website": result["website"]["value"] if "website" in result else "",
        }
        universities.append(university)

    return universities