from pydantic import BaseModel
from typing import Optional
from pydantic import Field


class ImageAnalysisResponse(BaseModel):
    image_type: Optional[str] = Field(
        description="""The type of the image or the category of image.
        This should be a single word or a phrase that describes the type of the image.
        Only return this if relevant to the user question.
        """
    )
    image_description: Optional[str] = Field(
        description="""The description of the image.
        This should be a concise description of the image.
        Only return this if relevant to the user question.
        """
    )
    extracted_data: Optional[str | list[str] | list[dict] | dict] = Field(
        default=None,
        description="""
        The extracted data from the image can be a single string, a list of
        strings, a list of row-objects (list[dict]), or a json object (dict).
        If output is of type dict then format the output as a clean and readable JSON object.
        """
    )
    structured_data: Optional[list[dict]] = Field(
        default=None,
        description="""
        Tabular/structured data extracted from the image, represented as a list
        of row dictionaries (each dict maps column name to cell value).
        Only return this if the image contains tabular data relevant to the user question.
        """
    )