# Changelog

- Convert SIRA, GeneralMessage, MessageForTransport, and MedicalDischarge dialogs to singletons.
- Add EVTWINDOWDESTROY handlers to clear references, preventing duplicate windows and leaked objects.
- Replace legacy menu popup handlers with NVDA script bindings that call a new GlobalPlugin.displayDialog helper.
- This helper uses wx.CallAfter for safe window restoration, minimization, and focusing.
- It also binds cleanup via partial to the onDestroy event.

Minor main.py cleanup:

- Removed queueHandler usage.
- Adjusted imports.

Bump add-on version to 2026.2.3 and update changelog/buildVars accordingly.
