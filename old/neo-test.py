from neo4j import GraphDatabase

uri = "bolt://babvs65.rothamsted.ac.uk:7687"
uri = "bolt://knetminer-wheat.cyverseuk.org:7687"
uri = "bolt://www.marcobrandizi.info:7687"

#uri = "bolt://knetminer-ara.cyverseuk.org:7687"
#driver = GraphDatabase.driver ( uri, auth = ( 'rouser', 'rouser' ) )

driver = GraphDatabase.driver ( uri )
def show_results ( tx ):
  qr = tx.run ( "MATCH (g:Gene) RETURN g LIMIT 25" )
  for r in qr:
    g = r [ 'g' ]
    print ( g [ 'identifier' ] )

with driver.session() as session:
  session.read_transaction ( show_results )
