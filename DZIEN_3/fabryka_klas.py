class ValidatorBase:
    @classmethod
    def create(cls,type_name:str,min_value:int,max_value:int):
        """ Twworzy klasę walidatora z przekrojowymi parametrami!"""
        class DynamicValidator(cls):
            TYPE = type_name

            def validate(self,value):
                if not(min_value<=value<=max_value):
                    raise ValueError(f"{value} is not valid for {type_name}!")

                return True
        return DynamicValidator

Range10 = ValidatorBase.create("Range10",10,20)
Range100 = ValidatorBase.create("Range100",100,200)

v1 = Range10()
v2 = Range100()

print(v1.validate(15))
print(v2.validate(150))
# print(v2.validate(450))

print(v1.TYPE)
print(v2.TYPE)
