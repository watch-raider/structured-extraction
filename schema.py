from pydantic import BaseModel, Field
from datetime import datetime

class CustomerAddress(BaseModel):
    zip_code: str = Field(description="Should contain the zip code alone")
    city: str = Field(description="Should hold the city name from the address")
    full_address: str = Field(description="Should hold the full address of the customer")




class PaymentInfo(BaseModel):
    due_date: datetime = Field(description="The due date of the credit card statement. Also known as the payment due "
                                           "date")
    minimum_payment: float = Field(description="the minimum amount that is due")
    new_balance: float = Field(description="the total new balance amount that can be paid")




class SpendLineItem(BaseModel):
    spend_date: datetime = Field(description="The date of the transaction. If the year part isn't mentioned in the "
                                             "line item explicitly, pick up the year from the statement date and use "
                                             "it instead.")
    spend_description: str = Field(description="The description of the spend")
    amount: float = Field(description="The amount of the transaction")




class ParsedCreditCardStatement(BaseModel):
    issuer_name: str = Field(description="What is the name of the issuer or the bank who has issued this credit card? "
                                         "I am not interested in the legal entity, but the primary brand name of the "
                                         "credit card.")
    customer_name: str = Field(description="What is the name of the customer to whom this credit card statement "
                                           "belongs to? Format the name of the customer well with the first letter of "
                                           "each name capitalized.")
    customer_address: CustomerAddress = Field(description="Since there might be multiple addresses in the context "
                                                          "provided to you, first gather all addresses. Try to "
                                                          "understand whom this credit card statement is being "
                                                          "addressed to or in other words, the name of the customer. "
                                                          "Find the address that matches that person's. Be sure to "
                                                          "return the customer's address, for whom this credit card "
                                                          "statement is for. Do not respond with any other address.")
    payment_info: PaymentInfo = Field(description="Payment information is important part of any credit card statement "
                                                  "and it consists of the new balance or the full amount due for the "
                                                  "current statement, the minimum payment due and the payment due "
                                                  "date.")
    spend_line_items: list[SpendLineItem] = Field(description="This credit card statement contains spending details "
                                                              "line items. Spend details can be split across the "
                                                              "provided context. Respond with details of all the "
                                                              "spend items by looking at the whole context always.")