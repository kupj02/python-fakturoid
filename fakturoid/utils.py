import time
from typing import Dict, List, Any, Optional

import requests

from fakturoid import Fakturoid, Subject, Invoice, InvoiceLine


def get_fakturoid_account(slug: str, client_id: str, client_secret: str) -> Fakturoid:
    """
    Initializes and returns a Fakturoid account instance.

    :param slug: The account slug used to identify the Fakturoid account.
    :param client_id: The Fakturoid client ID.
    :param client_secret: The Fakturoid client secret.
    :return: An initialized Fakturoid instance.
    """
    fa = Fakturoid(slug, client_id, client_secret)
    return fa


def create_fakturoid_subject(fa: Fakturoid, data: Dict[str, str]) -> Subject:
    """
    Field definitions here: https://www.fakturoid.cz/api/v3/subjects
    Creates or retrieves a Fakturoid subject (client or customer).

    :param fa: An authenticated Fakturoid instance.
    :param data: A dictionary containing subject information, such as:
                 - name: The client's name (required).
                 - email: The client's primary email (used to search for existing subjects).
                 - Additional fields for address, VAT, registration, delivery, and preferences.

    :return: A Fakturoid Subject instance representing the created or retrieved subject.
    """
    if data.get('email'):
        existing_subjects = fa.subjects.search(query=data['email'])
        for subject in existing_subjects:
            if subject.email == data['email']:
                return subject

    new_subject = Subject(
        custom_id=data.get('custom_id'),
        type=data.get('type'),
        name=data['name'],  # required
        full_name=data.get('full_name'),
        email=data.get('email'),
        email_copy=data.get('email_copy'),
        phone=data.get('phone'),
        web=data.get('web'),
        street=data.get('street'),
        city=data.get('city'),
        zip=data.get('zip'),
        country=data.get('country'),
        registration_no=data.get('registration_no'),
        vat_no=data.get('vat_no'),
        legal_form=data.get('legal_form'),
        vat_mode=data.get('vat_mode'),
        bank_account=data.get('bank_account'),
        iban=data.get('iban'),
        swift_bic=data.get('swift_bic'),
        variable_symbol=data.get('variable_symbol'),
        setting_update_from_ares=data.get('setting_update_from_ares', 'inherit'),
        ares_update=data.get('ares_update', True),  # deprecated, defaults to True
        setting_invoice_pdf_attachments=data.get('setting_invoice_pdf_attachments', 'inherit'),
        setting_estimate_pdf_attachments=data.get('setting_estimate_pdf_attachments', 'inherit'),
        setting_invoice_send_reminders=data.get('setting_invoice_send_reminders', 'inherit'),
        suggestion_enabled=data.get('suggestion_enabled', True),
        custom_email_text=data.get('custom_email_text'),
        overdue_email_text=data.get('overdue_email_text'),
        invoice_from_proforma_email_text=data.get('invoice_from_proforma_email_text'),
        thank_you_email_text=data.get('thank_you_email_text'),
        custom_estimate_email_text=data.get('custom_estimate_email_text'),
        webinvoice_history=data.get('webinvoice_history'),
        has_delivery_address=data.get('has_delivery_address', False),
        delivery_name=data.get('delivery_name'),
        delivery_street=data.get('delivery_street'),
        delivery_city=data.get('delivery_city'),
        delivery_zip=data.get('delivery_zip'),
        delivery_country=data.get('delivery_country'),
        due=data.get('due'),
        currency=data.get('currency'),
        language=data.get('language'),
        private_note=data.get('private_note'),
        local_vat_no=data.get('local_vat_no'),
    )

    if fa is not None:
        fa.save(new_subject)

    return new_subject


def create_fakturoid_invoice_lines(data: List[Dict[str, Any]]) -> List[InvoiceLine]:
    """
    Field definitions here: https://www.fakturoid.cz/api/v3/invoices#lines
    Creates a list of InvoiceLine objects for a Fakturoid invoice.

    :param data: A list of dictionaries containing line item details. Each dictionary can include:
                 - name: Description of the line item (required).
                 - quantity: Number of units for the line item (default 1).
                 - unit_price: Price per unit (required).
                 - unit_name: The unit's name (default 'ks').
                 - vat_rate: VAT rate for the item (default 0).
                 - unit_price_without_vat: Price per unit without VAT.
                 - unit_price_with_vat: Price per unit including VAT.
                 - inventory details and other financial fields as per Fakturoid's API specifications.

    :return: A list of populated InvoiceLine objects to be included in a Fakturoid invoice.
    """
    lines = []
    for line in data:
        lines.append(InvoiceLine(
            id=line.get('id'),
            name=line['name'],  # required
            quantity=line.get('quantity', 1),
            unit_name=line.get('unit_name', 'ks'),
            unit_price=line['unit_price'],  # required
            vat_rate=line.get('vat_rate', 0),
            unit_price_without_vat=line.get('unit_price_without_vat', line['unit_price']),
            unit_price_with_vat=line.get('unit_price_with_vat'),
            total_price_without_vat=line.get('total_price_without_vat'),
            total_vat=line.get('total_vat'),
            native_total_price_without_vat=line.get('native_total_price_without_vat'),
            native_total_vat=line.get('native_total_vat'),
            inventory_item_id=line.get('inventory_item_id'),
            sku=line.get('sku'),
            inventory=line.get('inventory', None)  # If inventory info provided
        ))

    return lines


def create_invoice(fa: Fakturoid, invoice_data: Dict[str, Any], lines: List[InvoiceLine]) -> Invoice:
    """
    Field definitions here: https://www.fakturoid.cz/api/v3/invoices
    Creates a Fakturoid Invoice object based on provided data and line items.

    :param fa: An authenticated Fakturoid instance.
    :param invoice_data: Dictionary containing invoice details. Key fields include:
                         - client details, payment methods, tax configurations, etc.
                         - Additional fields like due date, footer notes, attachments.

    :param lines: List of InvoiceLine objects generated by `create_fakturoid_invoice_lines`.

    :return: A populated Invoice object ready for saving or further processing.
    """
    invoice = Invoice(
        custom_id=invoice_data.get('custom_id'),
        document_type=invoice_data.get('document_type', 'invoice'),  # default to 'invoice'
        proforma_followup_document=invoice_data.get('proforma_followup_document'),
        tax_document_ids=invoice_data.get('tax_document_ids', []),
        correction_id=invoice_data.get('correction_id'),
        number=invoice_data.get('number'),
        number_format_id=invoice_data.get('number_format_id'),
        variable_symbol=invoice_data.get('variable_symbol'),
        your_name=invoice_data.get('your_name'),
        your_street=invoice_data.get('your_street'),
        your_city=invoice_data.get('your_city'),
        your_zip=invoice_data.get('your_zip'),
        your_country=invoice_data.get('your_country'),
        your_registration_no=invoice_data.get('your_registration_no'),
        your_vat_no=invoice_data.get('your_vat_no'),
        your_local_vat_no=invoice_data.get('your_local_vat_no'),
        client_name=invoice_data.get('client_name'),
        client_street=invoice_data.get('client_street'),
        client_city=invoice_data.get('client_city'),
        client_zip=invoice_data.get('client_zip'),
        client_country=invoice_data.get('client_country'),
        client_has_delivery_address=invoice_data.get('client_has_delivery_address', False),
        client_delivery_name=invoice_data.get('client_delivery_name'),
        client_delivery_street=invoice_data.get('client_delivery_street'),
        client_delivery_city=invoice_data.get('client_delivery_city'),
        client_delivery_zip=invoice_data.get('client_delivery_zip'),
        client_delivery_country=invoice_data.get('client_delivery_country'),
        client_registration_no=invoice_data.get('client_registration_no'),
        client_vat_no=invoice_data.get('client_vat_no'),
        client_local_vat_no=invoice_data.get('client_local_vat_no'),
        subject_id=invoice_data.get('subject_id'),
        subject_custom_id=invoice_data.get('subject_custom_id'),
        generator_id=invoice_data.get('generator_id'),
        related_id=invoice_data.get('related_id'),
        paypal=invoice_data.get('paypal', False),
        gopay=invoice_data.get('gopay', False),
        token=invoice_data.get('token'),
        status=invoice_data.get('status', 'open'),
        order_number=invoice_data.get('order_number'),
        issued_on=invoice_data.get('issued_on'),
        taxable_fulfillment_due=invoice_data.get('taxable_fulfillment_due'),
        due=invoice_data.get('due'),
        due_on=invoice_data.get('due_on'),
        sent_at=invoice_data.get('sent_at'),
        paid_on=invoice_data.get('paid_on'),
        reminder_sent_at=invoice_data.get('reminder_sent_at'),
        cancelled_at=invoice_data.get('cancelled_at'),
        uncollectible_at=invoice_data.get('uncollectible_at'),
        locked_at=invoice_data.get('locked_at'),
        webinvoice_seen_on=invoice_data.get('webinvoice_seen_on'),
        note=invoice_data.get('note'),
        footer_note=invoice_data.get('footer_note'),
        private_note=invoice_data.get('private_note'),
        tags=invoice_data.get('tags', []),
        bank_account_id=invoice_data.get('bank_account_id'),
        bank_account=invoice_data.get('bank_account'),
        iban=invoice_data.get('iban'),
        swift_bic=invoice_data.get('swift_bic'),
        iban_visibility=invoice_data.get('iban_visibility', 'automatically'),
        show_already_paid_note_in_pdf=invoice_data.get('show_already_paid_note_in_pdf', False),
        payment_method=invoice_data.get('payment_method', 'bank'),
        custom_payment_method=invoice_data.get('custom_payment_method'),
        hide_bank_account=invoice_data.get('hide_bank_account'),
        language=invoice_data.get('language', 'cz'),
        transferred_tax_liability=invoice_data.get('transferred_tax_liability', False),
        supply_code=invoice_data.get('supply_code'),
        oss=invoice_data.get('oss', 'disabled'),
        vat_price_mode=invoice_data.get('vat_price_mode', 'without_vat'),
        round_total=invoice_data.get('round_total', False),
        subtotal=invoice_data.get('subtotal'),
        total=invoice_data.get('total'),
        native_subtotal=invoice_data.get('native_subtotal'),
        native_total=invoice_data.get('native_total'),
        remaining_amount=invoice_data.get('remaining_amount'),
        remaining_native_amount=invoice_data.get('remaining_native_amount'),
        eet_records=invoice_data.get('eet_records', []),
        lines=lines,  # setting the invoice lines
        vat_rates_summary=invoice_data.get('vat_rates_summary', []),
        paid_advances=invoice_data.get('paid_advances', []),
        payments=invoice_data.get('payments', []),
        attachments=invoice_data.get('attachments', []),
    )

    if fa is not None:
        fa.save(invoice)

    return invoice


def update_invoice(fa: Fakturoid, invoice_id: int, updated_data: Dict[str, Any]) -> Invoice:
    """
    Update an existing Fakturoid invoice with the provided data.

    :param fa: Fakturoid instance
    :param invoice_id: ID of the invoice to be updated
    :param updated_data: Dictionary of data to update in the invoice
    :return: The updated Invoice object
    """
    invoice = fa.invoice(invoice_id)

    if not invoice:
        raise ValueError(f"Invoice with id {invoice_id} not found.")

    for field, value in updated_data.items():
        if hasattr(invoice, field):
            setattr(invoice, field, value)

    fa.save(invoice)
    return invoice


def delete_invoice(fa: Fakturoid, invoice_id: int) -> None:
    """
    Delete an invoice by its ID.

    :param fa: Fakturoid instance
    :param invoice_id: ID of the invoice to delete
    """
    invoice = fa.invoice(invoice_id)
    if invoice:
        fa.delete(invoice)
    else:
        raise ValueError(f"Invoice with id {invoice_id} not found.")


def get_fakturoid_invoice_pdf_url(invoice_id: int, slug: str):
    return 'https://app.fakturoid.cz/api/v3/accounts/{}/invoices/{}/download.pdf' \
        .format(slug, invoice_id)


def download_invoice_pdf(fa: Fakturoid, invoice_id: int, retry_delay: int = 2, max_retries: int = 5) -> Optional[bytes]:
    """
    Downloads an invoice PDF by its ID from Fakturoid.
    Implements retry logic in case the PDF is not immediately available.

    :param fa: Fakturoid instance
    :param invoice_id: The ID of the invoice in Fakturoid.
    :param retry_delay: The delay between retries in seconds.
    :param max_retries: The maximum number of retries before giving up.
    :return: The PDF content as bytes, or None if not available after retries.
    """
    url = get_fakturoid_invoice_pdf_url(invoice_id, fa.slug)
    fa._ensure_token()
    retries = 0
    headers = {
        'User-Agent': fa.user_agent,
        'Authorization': f'Bearer {fa.token}',
        'Accept': 'application/pdf'
    }

    while retries < max_retries:
        try:
            response = requests.get(
                url,
                stream=True,
                headers=headers,
            )
            if response.status_code == 200:
                return response.content
            elif response.status_code == 204:
                time.sleep(retry_delay)
                retries += 1
            else:
                response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise e
    return None
