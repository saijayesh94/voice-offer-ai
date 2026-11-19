"""
The PDFUpdater class provides functionalities to update text fields and checkboxes in the PDF
based on the provided data.
"""
from datetime import datetime, timedelta
import uuid
import os
import fitz
from third_party.mls.mls import MLS
from third_party.docu_sign.jwt_console import docu_sign
# from google.cloud import secretmanager
# from google.cloud import storage
import json

class PDFUpdater:
    """
     A class to update PDF files with the provided data.
    """
    def __init__(self, data, envelope_args):
        self.data = data
        self.mls_instance = MLS()
        self.mls_resp = None
        self.envelope_args = envelope_args
        self.secret_name = "projects/312724325377/secrets/maxhome-admin-creds/versions/1"

    def update_fields(self, doc, page_data):
        """
        Updates the fields in the given document based on the provided page data.

        Args:
            doc (fitz.Document): The document whose fields are to be updated.
            page_data (dict): A dictionary containing the page number as the key and 
            the fields to be updated as the value.
        """
        for page_num, fields in page_data.items():
            page = doc.load_page(int(page_num) - 1)
            widgets = page.widgets()

            for widget in widgets:
                field_name_widget = widget.field_name
                if field_name_widget in fields["fields"]:
                    field_info = fields["fields"][field_name_widget]
                    self.update_widget(widget, field_info)

    # def update_widget(self, widget, field_info):
    #     """
    #     Updates the given widget based on the provided field information.
    #     Args:
    #         widget (fitz.Widget): The widget to be updated.
    #         field_info (dict): A dictionary containing the field type and value to be updated in the widget.
    #     """
        
    #     if field_info["field_type"] == "text_field" and widget.field_type == 7:
    #         widget.text_fontsize = 12
    #         if self.mls_resp is not None:
    #             if field_info["mls_field"] is not None and field_info["mls_field"] in self.mls_resp and self.mls_resp[field_info["mls_field"]] is not None:
    #                 if isinstance(self.mls_resp[field_info["mls_field"]], list):
    #                     if field_info["mls_value"] in self.mls_resp[field_info["mls_field"]]:
    #                         widget.field_value = field_info["mls_value"]
    #                         widget.update()
    #                 else:
    #                     widget.field_value = str(self.mls_resp[field_info["mls_field"]])
    #                     widget.update()
    #             else:
    #                 widget.field_value = field_info["field_value"]
    #                 widget.update()
 
    #         else:
    #             widget.field_value = field_info["field_value"]
    #             widget.update()
    
    #     elif field_info["field_type"] == "checkbox" and widget.field_type == 2:
    #         if self.mls_resp is not None:
    #             if field_info["mls_field"] is not None and field_info["mls_field"] in self.mls_resp and self.mls_resp[field_info["mls_field"]] is not None:
    #                 if isinstance(self.mls_resp[field_info["mls_field"]], list):
    #                     if field_info["mls_value"] in self.mls_resp[field_info["mls_field"]]:
    #                         field_info["field_value"] = True
    #                         widget.field_value = field_info["field_value"]  # Directly Make it True
    #                         widget.update()
    #                 else:
    #                     field_info["field_value"] = True
    #                     widget.field_value = field_info["field_value"]  # Directly Make it True
    #                     widget.update()
    #             else:
    #                 widget.field_value = field_info["field_value"]
    #                 widget.update()

    #         else:
    #             widget.field_value = field_info["field_value"]
    #             widget.update()

    def update_widget(self, widget, field_info):
        """
        Updates the given widget based on the provided field information.
        Args:
            widget (fitz.Widget): The widget to be updated.
            field_info (dict): A dictionary containing the field type and value to be updated in the widget.
        """

        # if field_info["field_type"] == "text_field" and widget.field_type == 7:
        #     widget.text_fontsize = 10
        #     # widget.text_font = "Helv-Bold"
        #     if self.mls_resp is not None:
        #         if field_info["mls_field"] is not None and field_info["mls_field"] in self.mls_resp and self.mls_resp[field_info["mls_field"]] is not None:
        #             if isinstance(self.mls_resp[field_info["mls_field"]], list):
        #                 if field_info["mls_value"] in self.mls_resp[field_info["mls_field"]]:
        #                     widget.field_value = field_info["mls_value"].upper()
        #                     # widget._text_format.update({
        #                     #     "font": "Helv-Bold",
        #                     #     "fontsize": 16,
        #                     # })
        #                     widget.update()
        #             else:
        #                 widget.field_value = str(self.mls_resp[field_info["mls_field"]]).upper()
        #                 # widget._text_format.update({
        #                 #         "font": "Helv-Bold",
        #                 #         "fontsize": 16,
        #                 #     })
        #                 widget.update()
        #         else:
        #             widget.field_value = field_info["field_value"].upper()
        #             # widget._text_format.update({
        #             #             "font": "Helv-Bold",
        #             #             "fontsize": 16,
        #             #         })
        #             widget.update()
        #     else:
        #         widget.field_value = field_info["field_value"].upper()
        #         # widget._text_format.update({
        #         #                 "font": "Helv-Bold",
        #         #                 "fontsize": 16,
        #         #             })
        #         widget.update()

        if field_info["field_type"] == "text_field" and widget.field_type == 7:
            widget.text_fontsize = 10
            # widget.text_font = "Helv-Bold"
            if self.mls_resp is not None:
                if field_info["mls_field"] is not None and field_info["mls_field"] in self.mls_resp and self.mls_resp[field_info["mls_field"]] is not None:
                    if isinstance(self.mls_resp[field_info["mls_field"]], list):
                        if field_info["mls_value"] in self.mls_resp[field_info["mls_field"]]:
                            if field_info.get("is_price", False):
                                try:
                                    num = float(field_info["mls_value"])
                                    widget.field_value = f"{int(num):,}".upper()
                                except (ValueError, TypeError):
                                    widget.field_value = field_info["mls_value"].upper()
                            else:
                                widget.field_value = field_info["mls_value"].upper()
                            widget.update()
                    else:
                        if field_info.get("is_price", False):
                            try:
                                num = float(self.mls_resp[field_info["mls_field"]])
                                widget.field_value = f"{int(num):,}".upper()
                            except (ValueError, TypeError):
                                widget.field_value = str(self.mls_resp[field_info["mls_field"]]).upper()
                        else:
                            widget.field_value = str(self.mls_resp[field_info["mls_field"]]).upper()
                        widget.update()
                else:
                    if field_info.get("is_price", False):
                        try:
                            num = float(field_info["field_value"])
                            widget.field_value = f"{int(num):,}".upper()
                        except (ValueError, TypeError):
                            widget.field_value = field_info["field_value"].upper()
                    else:
                        widget.field_value = field_info["field_value"].upper()
                    widget.update()
            else:
                if field_info.get("is_price", False):
                    try:
                        num = float(field_info["field_value"])
                        widget.field_value = f"{int(num):,}".upper()
                    except (ValueError, TypeError):
                        widget.field_value = field_info["field_value"].upper()
                else:
                    widget.field_value = field_info["field_value"].upper()
                widget.update()


        elif field_info["field_type"] == "checkbox" and widget.field_type == 2:
            if self.mls_resp is not None:
                if field_info["mls_field"] is not None and field_info["mls_field"] in self.mls_resp and self.mls_resp[field_info["mls_field"]] is not None:
                    if isinstance(self.mls_resp[field_info["mls_field"]], list):
                        if field_info["mls_value"] in self.mls_resp[field_info["mls_field"]]:
                            field_info["field_value"] = True
                            widget.field_value = field_info["field_value"]
                            # widget._text_format.update({
                            #     "font": "Helv-Bold",
                            #     "fontsize": 16,
                            # })
                            widget.update()
                    else:
                        field_info["field_value"] = True
                        widget.field_value = field_info["field_value"]
                        # widget._text_format.update({
                        #         "font": "Helv-Bold",
                        #         "fontsize": 16,
                        #     })
                        widget.update()
                else:
                    widget.field_value = field_info["field_value"]
                    # widget._text_format.update({
                    #             "font": "Helv-Bold",
                    #             "fontsize": 16,
                    #         })
                    widget.update()
            else:
                widget.field_value = field_info["field_value"]
                # widget._text_format.update({
                #                 "font": "Helv-Bold",
                #                 "fontsize": 16,
                #             })
                widget.update()


    def access_secret_version(self):
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(name=self.secret_name)
        return response.payload.data.decode('UTF-8')
    
    def upload_file_to_gcs(self, bucket_name, file_path):
        sa_json_str = self.access_secret_version()
        sa_info = json.loads(sa_json_str)

        storage_client = storage.Client.from_service_account_info(sa_info)
        bucket = storage_client.get_bucket(bucket_name)
        unique_file_name = f"{uuid.uuid4()}-{os.path.basename(file_path)}"
        blob = bucket.blob(unique_file_name)
        blob.upload_from_filename(file_path, content_type='application/pdf')

        expiration = timedelta(hours=1)
        signed_url = blob.generate_signed_url(expiration=expiration)
        print(f"Uploaded file {os.path.basename(file_path)} to GCS bucket {bucket_name}")
        print(f"Signed URL: {signed_url}")
        return signed_url, unique_file_name
        
    def save_pdf(self, doc, filename):
        """Saves the given document as a PDF.

        Args:
            doc (fitz.Document): The document to save.
            filename (str): The name of the file to save the document as.
        """
        doc.save(filename)

    def process_files(self):
        """
        Processes files, updates fields based on MLS data or the provided data, saves as PDFs, and calls `docu_sign`.
        """
        self.mls_resp = self.mls_instance.fetch_property_details(self.data)
        # print("self.mls_resp:", self.mls_resp)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_folder = os.path.join("output_pdf", timestamp)
        os.makedirs(output_folder, exist_ok=True)
        uploaded_file = {}

        self.data["session_id"] = timestamp

        for file in self.data["files"]:
            doc = fitz.open(file["file_location"])
            self.update_fields(doc, file["pages"])

            output_path = os.path.join(output_folder, file["file_name"])
            self.save_pdf(doc, output_path)
            
            # signed_url, unique_file_name = self.upload_file_to_gcs("maxhomemailattachments", output_path)
            # uploaded_file = {
            #     "type": "Buyer's Agency Agreement",
            #     "fileName": unique_file_name
            # }
            
        docu_sign(self.envelope_args, self.data)
        return uploaded_file