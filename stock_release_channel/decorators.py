# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

delivery_date_generators = {}

delivery_date_steps = ["preparation", "delivery", "customer"]


def delivery_date_generator(step=None):
    def decorator(func):
        if step not in delivery_date_steps:
            raise Exception("Invalid decorator step")

        def check_object(*args, **kwargs):
            self = args[0]
            if self.__class__._name != "stock.release.channel":
                raise Exception(
                    "Decorator 'delivery_date_generator' can only be used on "
                    "a release channel"
                )
            return func(*args, **kwargs)

        delivery_date_generators.setdefault(step, []).append(check_object)

        return check_object

    return decorator
