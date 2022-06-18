## Courier - A Postman-like HTTP client in GTK+3

### Priority
- [ ] Add info property to treestore model
- [ ] Get collection name from info property
- [ ] Create method that converts treestire iter to dict
- [ ] Create method that writes dict to file on disk with postman_id as filename.json
- [ ] Write collection to file on importing using previously created method
- [ ] Add save button that writes current state of tree store model to files (overwriting existing ones)
- [ ] Detect changes to request tab and indicate unsaved change with something on the tab handle

### Secondary
- [ ] Add proper exception handling everywhere
- [ ] Add colors to HTTP verbs on tab handles
- [ ] Add breaks for misbehaviors on the UI (ex: send request with empty URL field)

### Future workable improvements
- [ ] Add query params tab to request
- [ ] Implement exporting existing collections
- [ ] Add new requests to existing collections
- [ ] Implement importing new collections
- [ ] Move loading collections to a new thread on startup
- [ ] Compatibility with more collection schema versions
- [ ] Environment system
- [ ] Upgrade libraries for GTK4 and libadwaita
