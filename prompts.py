from langchain.output_parsers import ResponseSchema

new_balance_schema = ResponseSchema(name="new_balance",
                             description="the total new balance amount that can be paid")
due_date_schema = ResponseSchema(name="due_date",
                                      description="the minimum amount that is due")
minimum_payment_schema = ResponseSchema(name="minimum_payment",
                                    description="the total new balance amount that can be paid")

response_schemas = [new_balance_schema, 
                    due_date_schema,
                    minimum_payment_schema]

review_template_2 = """\
For the following text, extract the following information:

new_balance: the total new balance amount that can be paid

due_date: the minimum amount that is due

minimum_payment: the total new balance amount that can be paid

text: {text}

{format_instructions}
"""