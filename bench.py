# Beta Ongoing Netlist Yielder(BONY): 
# Design for Automated Netlist Generator : DAG generator

# system imports 
from sys import argv
import random

from graphplot import exportGMLformat
# arg section
script, filename = argv

gateStates = ["NAND", "OR","XOR", "XNOR", "AND", "NOR"]
targetfile = open(filename, 'w')

# object: Design constraints for the design
class designConst:
	def __init__(self):
		self.max_fan_out 		= 3
		self.max_fan_in  		= 2
		self.stages 			= 5
		self.max_nodes_in_stage 	= 10
		self.min_nodes_in_stage 	= 7
		self.proxDepth			= 8
		self.IterationCount             = 5
		self.mainIterate		= 3
	def __del__(self):
		pass	
	
# object:  gate module design framework
class Gate:
	def __init__(self):
		self.serNum = 0 
		self.gateType = ''
		self.isInputNode = 0
		self.isOutputNode = 0
		self.fanInList = []
		self.fanOutList = []
	def __del__(self):
		pass	

# object: stage module design framework
class Stage:
	def __init__(self):
		self.numGates = 0
		self.totFanInRem = 0
		self.totFanOutRem = 0
		self.stageGates = []
	def __del__(self):
		pass	
	
# grows the entire graph structure		
def growGraph(stageModule):
	design = designConst()
	gateCount = 0
	for i in range(design.stages):
		stage = Stage()
		stage.numGates = random.randint(design.min_nodes_in_stage, design.max_nodes_in_stage)
		stageModule.append(stage)
		for j in range(stageModule[i].numGates):
			gate  = Gate()
			gateCount += 1
			gate.serNum = gateCount
			stageModule[i].stageGates.append(gate)
	return gateCount		
					
					
# sets the input-output nodes/pins for the graph schematic
#	- Assumption: The number of deep in-out nodes will be a random event: range(number of stages in the circuit)
def setInputOutputNodes(stageModule):
	design = designConst()
	# sets the input nodes : entire first stage is input though
	nodesInFirstStage = len(stageModule[0].stageGates)
	# first stage is input by default
	for first in range(nodesInFirstStage):
		stageModule[0].stageGates[first].isInputNode = 1
	# determines the number of deep input nodes
	detDeepInNodeCount = random.randint(0,design.stages-1) 
	for dNodeIn in range(detDeepInNodeCount):
		# determine the stage selection at random
		detStageIn = random.randint(0,design.stages-1)
		# determine the  stage selection at random
		detNodeIn = random.randint(0,len(stageModule[detStageIn].stageGates)-1)
		# set the selected node to an Deep Input Node stage
		stageModule[detStageIn].stageGates[detNodeIn].isInputNode = 1
	
	# sets the output nodes : entire output stage is output though
	nodesInLastStage = len(stageModule[design.stages-1].stageGates)
	# last stage is output by default
	for last in range(nodesInLastStage):
		stageModule[design.stages-1].stageGates[last].isInputNode = 0
		stageModule[design.stages-1].stageGates[last].isOutputNode = 1
	# deterine the number of deep output modules
	detDeepOutNodeCount = random.randint(0,design.stages-1) 	
	for dNodeOut in range(detDeepOutNodeCount):
		# determine the stage selection at random
		detStageOut = random.randint(0,design.stages-1)
		# determine the stage selection at random
		detNodeOut = random.randint(0,len(stageModule[detStageOut].stageGates)-1)
		# determine the selected node to a Deep Output Node stage
		if stageModule[detStageOut].stageGates[detNodeOut].isInputNode != 1: 
			# preference given for input node select over output node selection
			stageModule[detStageOut].stageGates[detNodeOut].isOutputNode = 1		


# generate optimal start and stop functions for the stage random allocation
def generateRandStartandEndPoints(appRandStart,appRandEnd):
	design = designConst()
	if appRandEnd - appRandStart > design.proxDepth:
		randStart = appRandStart
		randEnd = appRandStart + design.proxDepth
	else:
		randStart = appRandStart
		randEnd = appRandEnd

	return randStart,randEnd
		

# determine the interconnects: generate complete graph
# abandoned
def determineInterConnects(stageModule):
	design = designConst()
	# map the fan-out with single dimension for each node random process
	for i in range(len(stageModule)-1):
		for j in range(len(stageModule[i].stageGates)): 
			node = stageModule[i].stageGates[j]
			# map the fan-out with single dimension for each node random process
			#	-doesn't gurantee that every node has a fan-in or fanout
			#	- output nodes will not have any fan-out(s) and input nodes no fan-ins(s)
			#	-random map: gurantee max fan-in not violated: rerun of rand return node allocation			
			if not node.isOutputNode:			
				#allocRandStage = random.randint(i+1,design.stages-1) 
				randStart,randEnd = generateRandStartandEndPoints(i+1,design.stages-1)
				allocRandStage = random.randint(randStart,randEnd) 
				allocRandNode = random.randint(0,len(stageModule[allocRandStage].stageGates)-1)
				nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
				if not nodeConnect.isInputNode: 
					if (nodeConnect.serNum not in node.fanOutList) and (node.serNum not in nodeConnect.fanInList):
						if (len(node.fanOutList) < design.max_fan_out) and (len(nodeConnect.fanInList) < design.max_fan_in):
							node.fanOutList.append(nodeConnect.serNum)
							nodeConnect.fanInList.append(node.serNum)

	# map the fan-in with single dimension for each node random process
	for i in range(1,len(stageModule)):
		for j in range(len(stageModule[i].stageGates)): 
			node = stageModule[i].stageGates[j]
			# map the fan-in with single dimension for each node random process
			#	-doesn't gurantee that every node has a fan-in or fanout
			#	- output nodes will not have any fan-out(s) and input nodes no fan-ins(s)				 
			if not node.isInputNode:
				#allocRandStage = random.randint(0,i-1)	
				randStart,randEnd = generateRandStartandEndPoints(0,i-1)
				allocRandStage = random.randint(randStart,randEnd) 
				allocRandNode = random.randint(0,len(stageModule[allocRandStage].stageGates)-1)
				nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
				if not nodeConnect.isOutputNode:
					if (nodeConnect.serNum not in node.fanInList) and (node.serNum not in nodeConnect.fanOutList):
						if (len(node.fanInList) < design.max_fan_in) and (len(nodeConnect.fanOutList) < design.max_fan_out):
							node.fanInList.append(nodeConnect.serNum)
							nodeConnect.fanOutList.append(node.serNum)


# fast: determine the interconnects: generate complete graph	
def determineInterConnectsFast(stageModule):				
	design = designConst()
	# map the fan-out with single dimension for each node random process
	for i in range(len(stageModule)-1):
		for j in range(len(stageModule[i].stageGates)): 
			node = stageModule[i].stageGates[j]
			# map the fan-out with single dimension for each node random process
			#	-doesn't gurantee that every node has a fan-in or fanout
			#	- output nodes will not have any fan-out(s) and input nodes no fan-ins(s)
			#	-random map: gurantee max fan-in not violated: rerun of rand return node allocation			
			if not node.isOutputNode:			
				#allocRandStage = random.randint(i+1,design.stages-1) 
				randStart,randEnd = generateRandStartandEndPoints(i+1,design.stages-1)
				allocRandStage = random.randint(randStart,randEnd) 				
				
				allocRandNode = random.randint(0,len(stageModule[allocRandStage].stageGates)-1)
				nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
				if not nodeConnect.isInputNode: 
					if (nodeConnect.serNum not in node.fanOutList) and (node.serNum not in nodeConnect.fanInList):
						if (len(node.fanOutList) < design.max_fan_out) and (len(nodeConnect.fanInList) < design.max_fan_in):
							node.fanOutList.append(nodeConnect.serNum)
							nodeConnect.fanInList.append(node.serNum)							
			
			# map the fan-in with single dimension for each node random process
			if not node.isInputNode:
				#allocRandStage = random.randint(0,i-1)	
				randStart,randEnd = generateRandStartandEndPoints(0,i-1)
				allocRandStage = random.randint(randStart,randEnd) 				
				
				allocRandNode = random.randint(0,len(stageModule[allocRandStage].stageGates)-1)
				nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
				if not nodeConnect.isOutputNode:
					if (nodeConnect.serNum not in node.fanInList) and (node.serNum not in nodeConnect.fanOutList):
						if (len(node.fanInList) < design.max_fan_in) and (len(nodeConnect.fanOutList) < design.max_fan_out):
							node.fanInList.append(nodeConnect.serNum)
							nodeConnect.fanOutList.append(node.serNum)				


# stage analysis for free fanin and fanouts that can be accomodated for a complete connected network
def normalizeInterconnects(stageModule):
	design = designConst()
	remFO = []
	remFI = []
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)): 
			node = stageModule[i].stageGates[j]	
			if not node.isOutputNode:
				if not len(node.fanOutList):
					remFO.append(node.serNum)					
					allocRandStage = random.randint(i+1,design.stages-1) 
					allocRandNode = random.randint(0,len(stageModule[allocRandStage].stageGates)-1)
					nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
					if not nodeConnect.isInputNode: 
						if (nodeConnect.serNum not in node.fanOutList) and (node.serNum not in nodeConnect.fanInList):
							if (len(node.fanOutList) < design.max_fan_out) and (len(nodeConnect.fanInList) < design.max_fan_in):
								node.fanOutList.append(nodeConnect.serNum)
								nodeConnect.fanInList.append(node.serNum)	
			if not node.isInputNode:
				if not len(node.fanInList):
					remFI.append(node.serNum)
					allocRandStage = random.randint(0,i-1)	
					allocRandNode = random.randint(0,len(stageModule[allocRandStage].stageGates)-1)
					nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
					if not nodeConnect.isOutputNode:
						if (nodeConnect.serNum not in node.fanInList) and (node.serNum not in nodeConnect.fanOutList):
							if (len(node.fanInList) < design.max_fan_in) and (len(nodeConnect.fanOutList) < design.max_fan_out):
								node.fanInList.append(nodeConnect.serNum)
								nodeConnect.fanOutList.append(node.serNum)						
							
	return remFO,remFI


# generates the random gate criteria by suffle mode					
def randomGateState():
	random.shuffle(gateStates)
	return gateStates[0]		# returns the first gate always	
	
# allocate the gate notation to the nodes in the circuit		
def allocateGateNotation(stageModule):
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isInputNode:
				pass
			else:
				if len(node.fanInList) == 1:	# inverter probable
					node.gateType = 'NOT'	
				else:
					node.gateType = randomGateState()

# generate the automated schematic framework
def generateBenchMarkCircuit(stageModule):
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isInputNode:
				line = "INPUT (" + str(node.serNum) +")" +"\n"
				targetfile.write(line)				

	targetfile.write('\n\n')	
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isOutputNode:
				line = "OUTPUT (" + str(node.serNum) +")"+"\n"
				targetfile.write(line)
				
	targetfile.write('\n\n')					
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if not node.isInputNode: 			
				line = str(node.serNum) +" = "+ node.gateType + "("
				for fanInRange in range(len(node.fanInList)):
					if fanInRange == len(node.fanInList)-1:
						line += str(node.fanInList[fanInRange])
					else:
						line += str(node.fanInList[fanInRange]) +","	
				line += ")\n"
				targetfile.write(line)						
				

# non random : normalize method: 
def nonRandomNormalize(stageModule,remFO,remFI):
	print "It Wont work _critic :P "
	
# iterative chance solver and final normalization method:
def iterateSolveandNormalize(stageModule):
	design = designConst()
	remFO = []
	remFI = []
	for i in range(1,design.IterationCount):
		remFO,remFI = normalizeInterconnects(stageModule)
	if not len(remFO) and not len(remFI):
		print "design sucess!"
		allocateGateNotation(stageModule)
		generateBenchMarkCircuit(stageModule)
		#exportGMLformat(stageModule)
		return True
	else:
		print "design fail!"
		print 	remFO,remFI					
		nonRandomNormalize(stageModule,remFO,remFI)
		return False
		
# deign framework : pretty much everything designed here : DAG generation mapping and allocation
def designFramework(stageModule):
	design = designConst()
	setInputOutputNodes(stageModule)
	#determineInterConnects(stageModule)
	determineInterConnectsFast(stageModule)	
	for i in range(0,design.mainIterate):	
		status = iterateSolveandNormalize(stageModule)
		if status == True:
			break

# simple graph traversal function : printing the ser num of the nodes in graph
def traverseGraph(stageModule):
	design = designConst()
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			print node.serNum,"[stage]",i,"in",node.isInputNode,"out",node.isOutputNode, "fanOutList:",node.fanOutList," fanInList:",node.fanInList	
def main():
	stageModule = []
	totGates = 0
	totGates = growGraph(stageModule)				# grow the graph using nested lists
	designFramework(stageModule)
	print " The total number of gates: ",totGates
	#traverseGraph(stageModule)				 	# traverse the entire graph	
	targetfile.close()

if __name__ == '__main__':
	main()


