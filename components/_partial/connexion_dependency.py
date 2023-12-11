import connexion
from connexion.middleware.main import API
from connexion.options import SwaggerUIOptions
from connexion.exceptions import ResolverError
from connexion.resolver import Resolver


class ConnexionDependency:
    connexion = connexion
    SwaggerUIOptions = SwaggerUIOptions
    API = API
    ResolverError = ResolverError
    Resolver = Resolver
