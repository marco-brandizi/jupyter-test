from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship
import networkx as nx


def cypher2graph ( records, node_name_prop = None, rel_name_prop = None ):
	"""
	Credits: https://stackoverflow.com/a/59305794/529286
	
	Constructs a networkx graph from the results of a neo4j cypher query.
	Example of use:
	>>> result = session.run(query)
	>>> G = cypher2graph(result)

	Nodes have fields 'labels' (frozenset) and 'properties' (dicts). Node IDs correspond to the neo4j graph.
	Edges have fields 'type_' (string) denoting the type of relation, and 'properties' (dict)."""

	G = nx.MultiDiGraph()
	def add_node(node):
		# Adds node id it hasn't already been added
		attrs = dict ( node )
		id = attrs [ node_name_prop ] if node_name_prop and node_name_prop in attrs [ node_name_prop ] \
			   else node.id
		if G.has_node(id): return
		G.add_node(id, attr_dict = attrs )

	def add_edge(relation):
		# Adds edge if it hasn't already been added.
		# Make sure the nodes at both ends are created
		for node in (relation.start_node, relation.end_node):
			add_node ( node )
		# Check if edge already exists
		u = relation.start_node.id
		v = relation.end_node.id
		eid = relation.id
		if G.has_edge(u, v, key=eid):
			return
		
		# If not, create it
		attrs = dict ( relation )
		if rel_name_prop and rel_name_prop in attrs : 
			attrs [ 'label' ] = attrs [ rel_name_prop ]			

		G.add_edge ( u, v, eid, attr_dict = dict ( relation ) )

	for record in records:
		for entry in record.values():
			# Parse node
			if isinstance(entry, Node):
				add_node(entry)

			# Parse link
			elif isinstance(entry, Relationship):
				add_edge(entry)
			else:
				raise TypeError("Unrecognized object")
	return G

def demo():
	cypher = \
	"""MATCH (bp:BioProc{prefName:"Brassinosteroid Mediated Signaling Pathway"})
			<- [part:participates_in] - (rprotein:Protein)
			-  [xr:h_s_s|xref|ortho*0..1] - (protein:Protein)
			<-  [enc:enc] - (gene:Gene)
			- [occ:occ_in] -> (pub:Publication)
	WHERE toFloat ( occ.TFIDF ) > 20
	RETURN DISTINCT gene, occ, pub 
	LIMIT 20
	"""

	driver = GraphDatabase.driver( "bolt://babvs65.rothamsted.ac.uk:7688", auth = ( "rouser", "rouser" ) )
	session = driver.session()
	result = session.run( cypher )

	#import netwulf as nw
	#g = cypher2graph( result, "prefName" )
	#nw.visualize ( g )
	import textwrap as tw

	g = nx.MultiDiGraph()
	for record in result:
		gene = record [ "gene" ]
		gid = gene [ "prefName" ]

		pub = record [ "pub" ]
		pid = pub [ "AbstractHeader" ]
		pid = tw.shorten ( pid, width = 35, fix_sentence_endings = True, placeholder = '...' ) \
			    + " " + pub [ "prefName" ]
		#pid = pub [ "prefName" ]

		g.add_node ( gid )
		g.add_node ( pid ) 
		g.add_edge ( gid, pid )
	
	nx.draw_graphviz (g, pos = nx.spring_layout(g), with_labels = True )
	#input ( "Done! Press a [CR]" )

	#import netwulf as nw
	#nw.visualize ( g )

if __name__ == "__main__":
	demo()
