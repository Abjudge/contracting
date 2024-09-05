(() => {
  // ../trigger_contracting/trigger_contracting/public/js/form/formatters.js
  frappe.form.link_formatters["Business Item"] = function(value, doc) {
    consolejson.log("value", value);
    if (doc.business_item_name && doc.business_item_name !== value) {
      return value + ": " + doc.business_item_name;
    } else {
      return value;
    }
  };
})();
//# sourceMappingURL=deskformat.bundle.7XBUDV3Z.js.map
