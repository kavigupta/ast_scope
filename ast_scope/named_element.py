
import abc

class NamedElement(abc.ABC):
    @abc.abstractmethod
    def name(self):
        pass
