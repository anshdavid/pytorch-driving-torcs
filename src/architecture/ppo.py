import numpy


class PPOMemory:
    def __init__(self, batch_size):

        self.states = []
        self.probs = []
        self.vals = []
        self.actions = []
        self.rewards = []
        self.dones = []

        self.batch_size = batch_size

    def generate_batches(self):
        n_states = len(self.states)
        batch_start = numpy.arange(0, n_states, self.batch_size)
        indices = numpy.arange(n_states, dtype=numpy.uint)
        numpy.random.shuffle(indices)
        batches = [indices[i : i + self.batch_size] for i in batch_start]

        return (
            numpy.array(self.states),
            numpy.array(self.actions),
            numpy.array(self.probs),
            numpy.array(self.vals),
            numpy.array(self.rewards),
            numpy.array(self.dones),
            batches,
        )

    def store_memory(self, state, action, probs, vals, reward, done):
        self.states.append(state)
        self.actions.append(action)
        self.probs.append(probs)
        self.vals.append(vals)
        self.rewards.append(reward)
        self.dones.append(done)

    def clear_memory(self):
        self.states = []
        self.probs = []
        self.actions = []
        self.rewards = []
        self.dones = []
        self.vals = []
