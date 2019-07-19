from abc import ABC, abstractmethod
import dash_core_components as dcc
import dash_html_components as html
import uuid
from itertools import chain
from dash.dependencies import Input, Output


class PythonComponent(ABC):
    def __init__(self):
        """
        Inputs and outputs are dash_core Store components, defining what information this component listens to, and
        what it produces
        """

        # Store inputs and outputs as a dictionary
        # self.inputs = {store.id: store for store in inputs}
        # self.outputs = {store.id: store for store in outputs}
        self.inputs = {}
        self.outputs = {}

        # Make this component have a random ID
        self.id = str(uuid.uuid4())

    @staticmethod
    def box(value):
        return dict(value=value)

    @staticmethod
    def unbox(value):
        return value['value']

    def define_input(self, name, default):
        self.inputs[name] = dcc.Store('{}-input-{}'.format(self.id, name), data=default)

    def define_output(self, name, default):
        self.outputs[name] = dcc.Store('{}-output-{}'.format(self.id, name), data=default)

    def layout(self, *args, **kwargs):
        """
        Renders the base component, which includes the stores, and a template that will be filled by the render() output
        """
        return html.Div(
            [html.Div(id=self.id)] + self.state_components()
        )

    @abstractmethod
    def render(self, *args):
        """
        Function that takes this components inputs and returns some Dash components
        :param args: List of input values
        """
        pass

    def state_components(self):
        return list(self.inputs.values()) + list(self.outputs.values())

    @abstractmethod
    def setup_callbacks(self, app):
        """
        Called once the app has been initialized with a layout. This is the only time the component should add
        callbacks
        """

        @app.callback(
            Output(self.id, 'children'),
            [Input(input.id, 'data') for input in self.inputs.values()]
        )
        def update_layout(*args, **kwargs):
            return self.render(*args, app=app)
