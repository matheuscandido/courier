## Courier - A Postman-like HTTP client in GTK+3

### To-Do

- [x] Load collections into a proper tree view on sidebar
    - [x] Pretty renderer for colored method verbs
    - [x] Collection v2.1 full spec parser
    - [-] Link treestore with collection dict in memory to open requests filled
- [x] Click on request in the sidebar and open it on a new tab
- [ ] Implement importing new collections
- [ ] Editing and saving open requests
- [ ] Add new requests to existing collections
- [ ] Implement exporting existing collections
- [ ] Add colors to HTTP verbs on tab handles
- [ ] Add proper exception handling everywhere
- [ ] Add breaks for misbehaviors on the UI (ex: send request with empty URL field)
- [ ] Add query params tab to request
- [ ] Move loading collections to a new thread on startup
