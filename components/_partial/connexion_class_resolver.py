import inspect
import typing as t
from connexion.resolver import Resolver
from connexion.exceptions import ResolverError


class ConnexionClassResolver(Resolver):
    """
    Resolves endpoint functions based on Flask's MethodView semantics, e.g.

    .. code-block:: yaml

        paths:
            /foo_bar:
                get:
                    operationId: "module:FooBarView.get"


    .. code-block:: python

        class FooBarView(MethodView):
            def get(self):
                return ...
            def post(self):
                return ...

    """

    _class_arguments_type = t.Dict[
        str, t.Dict[str, t.Union[t.Iterable, t.Dict[str, t.Any]]]
    ]

    def __init__(
        self,
        root_path,
        class_arguments: _class_arguments_type = None,
    ):
        """
        :param root_path: The root path relative to which an operationId is resolved.
            Can also be a module. Has the same effect as setting
            `x-swagger-router-controller` or `x-openapi-router-controller` equal to
            `root_path` for every operation individually.
        :type root_path: typing.Union[str, types.ModuleType]
        :param class_arguments: Arguments to instantiate the View Class in the format below

        .. code-block:: python

            {
              "ViewName": {
                "args": (positional arguments,)
                "kwargs": {
                  "keyword": "argument"
                }
              }
            }
        """

        super().__init__()
        self.class_arguments = class_arguments or {}
        self.initialized_views: list = []
        if inspect.ismodule(root_path):
            self.root_path = root_path.__name__
        else:
            self.root_path = root_path

    def resolve_operation_id(self, operation):
        """
        Resolves the operationId based on a special structure
        <module>:<class>.<method>

        Once resolved, completes the module relative to the root path, unless
        x-swagger-router-controller or x-openapi-router-controller is specified.

        :param operation: The operation to resolve
        :type operation: connexion.operations.AbstractOperation
        """

        operation_id = operation.operation_id
        module_name, method_object = str(operation_id).split(":", 1)
        class_name, meth_name = method_object.split(".", 1)
        # class_name = camelize(class_name)
        root_path = operation.router_controller or self.root_path

        return f"{root_path}.{module_name}.{class_name}.{meth_name}"

    def resolve_function_from_operation_id(self, operation_id: str):
        """
        Invokes the function_resolver

        :type operation_id: str
        """

        try:
            module_name, class_name, meth_name = operation_id.rsplit(".", 2)
            mod = __import__(module_name, fromlist=[class_name])
            view_cls = getattr(mod, class_name)
            # find the view and return it
            return self.resolve_method_from_class(class_name, meth_name, view_cls)

        except ImportError as e:
            msg = 'Cannot resolve operationId "{}"! Import error was "{}"'.format(
                operation_id, str(e)
            )
            raise ResolverError(msg)
        except (AttributeError, ValueError) as e:
            raise ResolverError(str(e))

    def resolve_method_from_class_as_view(self, view_name, meth_name, view_cls):
        view = None
        for v in self.initialized_views:
            # views returned by <class>.as_view
            # have the origin class attached as .view_class
            if v.view_class == view_cls:
                view = v
                break
        if view is None:
            # get the args and kwargs for this view
            cls_arguments = self.class_arguments.get(view_name, {})
            cls_args = cls_arguments.get("args", ())
            cls_kwargs = cls_arguments.get("kwargs", {})
            # call as_view to get a view function
            # that is decorated with the classes
            # decorator list, if any
            view = view_cls.as_view(view_name, *cls_args, **cls_kwargs)
            # add the view to the list of initialized views
            # in order to call as_view only once
            self.initialized_views.append(view)
        # return the class as view function
        # for each operation so that requests
        # are dispatched with <class>.dispatch_request,
        # when calling the view function
        return view

    def resolve_method_from_class(self, view_name, meth_name, view_cls):
        view = None
        for v in self.initialized_views:
            if v.__class__ == view_cls:
                view = v
                break
        if view is None:
            # get the args and kwargs for this view
            cls_arguments = self.class_arguments.get(view_name, {})
            cls_args = cls_arguments.get("args", ())
            cls_kwargs = cls_arguments.get("kwargs", {})
            # instantiate the class with the args and kwargs
            view = view_cls(*cls_args, **cls_kwargs)
            self.initialized_views.append(view)
        # get the method if the class
        func = getattr(view, meth_name)
        # Return the method function of the class
        return func
