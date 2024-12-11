#!/usr/bin/env python3
import netsquid as ns
from netsquid.nodes import Node
from netsquid.protocols import Protocol
from netsquid.protocols import NodeProtocol
from netsquid.components import QuantumChannel
from netsquid.nodes import Node, DirectConnection
from netsquid.qubits import qubitapi as qapi
from netsquid.components.models.delaymodels import FibreDelayModel

#protocol to create the qubit and then send it from alice to bob
class StateTransferProtocol(NodeProtocol):
    def run(self):
        if self.node.name == "Alice":
           qubit, = qapi.create_qubits(1)
           print("Alice created a qubit: ")
           print(qubit.qstate.qrepr)
           self.node.ports["qout"].tx_output(qubit)
        elif self.node.name == "Bob":
           print(f"{self.node.name}: Waiting for qubit...")
           port = self.node.ports["qin"]
           yield self.await_port_input(port)
           qubitState = port.rx_input().items[0]
           print("Bob recieved a qubit:")
           print(qubitState.qstate.qrepr)


#creates the two nodes and the channel between them
alice = Node("Alice", port_names=["qout"])
bob = Node("Bob", port_names=["qin"])
q_channel = QuantumChannel("quantum_channel", length=1e-3, models={"delay_model": FibreDelayModel()})
alice.ports["qout"].connect(q_channel.ports["send"])
bob.ports["qin"].connect(q_channel.ports["recv"])

#initialize the protocol with alice and bob
alice_protocol = StateTransferProtocol(alice)
bob_protocol = StateTransferProtocol(bob)

#start the protocols
print("Starting protocols...")
alice_protocol.start()
bob_protocol.start()

# Run the simulation
print("Running simulation...")
ns.sim_run()

ns.sim_run()