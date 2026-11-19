import base64, os
from os import path

from docusign_esign import EnvelopesApi, EnvelopeDefinition, Document, Signer, CarbonCopy, SignHere, Tabs, Recipients

from ...consts import demo_docs_path, pattern
from ...jwt_helpers import create_api_client


class Eg002SigningViaEmailController:

    @classmethod
    def worker(cls, args, config_dict, file_info):
        """
        1. Create the envelope request object
        2. Send the envelope
        """

        #ds-snippet-start:eSign2Step3
        envelope_args = args["envelope_args"]
        # Create the envelope request object
        envelope_definition = cls.make_envelope(envelope_args, config_dict, file_info)
        api_client = create_api_client(base_path=args["base_path"], access_token=args["access_token"])
        # Call Envelopes::create API method
        # Exceptions will be caught by the calling function
        envelopes_api = EnvelopesApi(api_client)
        results = envelopes_api.create_envelope(account_id=args["account_id"], envelope_definition=envelope_definition)

        envelope_id = results.envelope_id

        return {"envelope_id": envelope_id}
        #ds-snippet-end:eSign2Step3

    @classmethod
    #ds-snippet-start:eSign2Step2
    def make_envelope(cls, args, config_dict, file_info):
        """
        Creates envelope
        Document 1: An HTML document.
        Document 2: A Word .docx document.
        Document 3: A PDF document.
        DocuSign will convert all of the documents to the PDF format.
        The recipients" field tags are placed using <b>anchor</b> strings.
        """

        env = EnvelopeDefinition(
            email_subject="Please sign this document set"
        )

        dym_path = os.path.join(demo_docs_path, config_dict["session_id"])
        with open(path.join(dym_path, file_info["file_name"]), "rb") as file:
                doc_pdf_bytes = file.read()
        doc_b64 = base64.b64encode(doc_pdf_bytes).decode("ascii")

        document3 = Document(  # create the DocuSign document object
            document_base64=doc_b64,
            name="Lorem Ipsum",  # can be different from actual file name
            file_extension="pdf",  # many different document types are accepted
            document_id="3"  # a label used to reference the doc
        )
        
        env.documents = [document3]
        

        # Create the signer recipient model
        signer1 = Signer(
            email=args["signer_email"],
            name=args["signer_name"],
            recipient_id="1",
            routing_order="1"
        )
        # routingOrder (lower means earlier) determines the order of deliveries
        # to the recipients. Parallel routing order is supported by using the
        # same integer as the order for two or more recipients.

        # create a cc recipient to receive a copy of the documents
        cc1 = CarbonCopy(
            email=args["cc_email"],
            name=args["cc_name"],
            recipient_id="2",
            routing_order="1"
        )

        # Create signHere fields (also known as tabs) on the documents,
        # We"re using anchor (autoPlace) positioning
        #
        # The DocuSign platform searches throughout your envelope"s
        # documents for matching anchor strings. So the
        # signHere2 tab will be used in both document 2 and 3 since they
        # use the same anchor string for their "signer 1" tabs.
        sign_here1 = SignHere(
            anchor_string="**signature_1**",
            anchor_units="pixels",
            anchor_y_offset="10",
            anchor_x_offset="20"
        )

        sign_here2 = SignHere(
            anchor_string="/sn1/",
            anchor_units="pixels",
            anchor_y_offset="10",
            anchor_x_offset="20"
        )

        # Add the tabs model (including the sign_here tabs) to the signer
        # The Tabs object wants arrays of the different field/tab types
        signer1.tabs = Tabs(sign_here_tabs=[sign_here1, sign_here2])

        # Add the recipients to the envelope object
        recipients = Recipients(signers=[signer1], carbon_copies=[cc1])
        env.recipients = recipients

        # Request that the envelope be sent by setting |status| to "sent".
        # To request that the envelope be created as a draft, set to "created"
        env.status = args["status"]

        return env

    @classmethod
    def create_document1(cls, args):
        """ Creates document 1 -- an html document"""

        return f"""
        <!DOCTYPE html>
        <html>
            <head>
              <meta charset="UTF-8">
            </head>
            <body style="font-family:sans-serif;margin-left:2em;">
            <h1 style="font-family: "Trebuchet MS", Helvetica, sans-serif;
                color: darkblue;margin-bottom: 0;">World Wide Corp</h1>
            <h2 style="font-family: "Trebuchet MS", Helvetica, sans-serif;
              margin-top: 0px;margin-bottom: 3.5em;font-size: 1em;
              color: darkblue;">Order Processing Division</h2>
            <h4>Ordered by {args["signer_name"]}</h4>
            <p style="margin-top:0em; margin-bottom:0em;">Email: {args["signer_email"]}</p>
            <p style="margin-top:0em; margin-bottom:0em;">Copy to: {args["cc_name"]}, {args["cc_email"]}</p>
            <p style="margin-top:3em;">
                Candy bonbon pastry jujubes lollipop wafer biscuit biscuit. Topping brownie sesame snaps sweet roll pie. 
                Croissant danish biscuit soufflé caramels jujubes jelly. Dragée danish caramels lemon drops dragée. 
                Gummi bears cupcake biscuit tiramisu sugar plum pastry. Dragée gummies applicake pudding liquorice. 
                Donut jujubes oat cake jelly-o. 
                Dessert bear claw chocolate cake gummies lollipop sugar plum ice cream gummies cheesecake.
            </p>
            <!-- Note the anchor tag for the signature field is in white. -->
            <h3 style="margin-top:3em;">Agreed: <span style="color:white;">**signature_1**/</span></h3>
            </body>
        </html>
        """
    #ds-snippet-end:eSign2Step2

            # files_array =[]
        # for i in config:
           # Read session/filename 
            #    with open(path.join(demo_docs_path, doc_pdf_path), "rb") as file:
            #     doc3_pdf_bytes = file.read()
            # doc3_b6644 = base64.b64encode(doc3_pdf_bytes).decode("ascii")
        #     document3 = Document(  # create the DocuSign document object
        #     document_base64=doc3_b64,
        #     name="Lorem Ipsum",  # can be different from actual file name
        #     file_extension="pdf",  # many different document types are accepted
        #     document_id="3"  # a label used to reference the doc
        # )
            # append doc3_b6644 to global files_array
