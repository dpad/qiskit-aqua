import unittest

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.qobj import RunConfig
from qiskit.providers.aer.noise import NoiseModel

from test.common import QiskitAquaTestCase
from qiskit.aqua import QuantumInstance, get_aer_backend


def _compare_dict(dict1, dict2):
    equal = True
    for key1, value1 in dict1.items():
        if key1 not in dict2:
            equal = False
            break
        if value1 != dict2[key1]:
            equal = False
            break
    return equal


class TestSkipQobjValidation(QiskitAquaTestCase):

    def setUp(self):
        super().setUp()
        self.random_seed = 10598

        qr = QuantumRegister(2)
        cr = ClassicalRegister(2)
        qc = QuantumCircuit(qr, cr)
        qc.h(qr[0])
        qc.cx(qr[0], qr[1])
        # Ensure qubit 0 is measured before qubit 1
        qc.barrier(qr)
        qc.measure(qr[0], cr[0])
        qc.barrier(qr)
        qc.measure(qr[1], cr[1])

        self.qc = qc
        self.backend = get_aer_backend('qasm_simulator')
        self.run_config = RunConfig(seed=self.random_seed, shots=1024)

    def test_wo_backend_options(self):
        quantum_instance = QuantumInstance(self.backend, seed_mapper=self.random_seed, run_config=self.run_config)
        # run without backend_options and without noise
        res_wo_bo = quantum_instance.execute(self.qc).get_counts(self.qc)

        quantum_instance.skip_qobj_validation = True
        res_wo_bo_skip_validation = quantum_instance.execute(self.qc).get_counts(self.qc)
        self.assertTrue(_compare_dict(res_wo_bo, res_wo_bo_skip_validation))

    def test_w_backend_options(self):
        # run with backend_options
        quantum_instance = QuantumInstance(self.backend, seed_mapper=self.random_seed, run_config=self.run_config,
                                           backend_options={'initial_statevector': [.5, .5, .5, .5]})
        res_w_bo = quantum_instance.execute(self.qc).get_counts(self.qc)
        quantum_instance.skip_qobj_validation = True
        res_w_bo_skip_validation = quantum_instance.execute(self.qc).get_counts(self.qc)
        self.assertTrue(_compare_dict(res_w_bo, res_w_bo_skip_validation))

    def test_w_noise(self):
        # build noise model
        # Asymetric readout error on qubit-0 only
        probs_given0 = [0.9, 0.1]
        probs_given1 = [0.3, 0.7]
        noise_model = NoiseModel()
        noise_model.add_readout_error([probs_given0, probs_given1], [0])

        quantum_instance = QuantumInstance(self.backend, seed_mapper=self.random_seed, run_config=self.run_config,
                                           noise_model=noise_model)
        res_w_noise = quantum_instance.execute(self.qc).get_counts(self.qc)

        quantum_instance.skip_qobj_validation = True
        res_w_noise_skip_validation = quantum_instance.execute(self.qc).get_counts(self.qc)
        self.assertTrue(_compare_dict(res_w_noise, res_w_noise_skip_validation))


if __name__ == '__main__':
    unittest.main()