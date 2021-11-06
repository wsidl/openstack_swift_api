
export const state = () => ({
  objects: [],
})

export const getters = {
  getObject: (state) => (id) => {
    return state.objects.find(o => o.id === id);
  }
}

export const mutations = {
  addObjects (state, newObjects) {
    state.objects = newObjects;
  },
  setTag(state, {object_id, tagName, tagValue}){

    state.objects.find(o => o.id === object_id).metadata.push([tagName, tagValue]);
  },
  deleteTag(state, {object_id, tagName, tagValue}){
    let obj = state.objects.find(o => o.id === object_id);
    let index = obj.metadata.findIndex(t => t[0]===tagName&&t[1]===tagValue);
    if(index > -1)obj.metadata.splice(index, 1);
  },
  saveName(state, {object_id, name}) {
    state.objects.find(o => o.id === object_id).name = name;
  },
  deleteObject(state, object_id){
    state.objects.splice(
      state.objects.findIndex(o => o.id===object_id),
      1
    );
  }
}

export const actions = {
  getObjects({commit}) {
    // commit("addObjects", [
    //   {id: 1, name: "test", metadata: [["type", "text"], ["value", "env"]], size: 237, updated: '2021-09-23 13:49:57'},
    //   {id: 2, name: "test2", metadata: [["type", "text"], ["value", "env"]], size: 23657, updated: '2021-23-11 05:18:02'}
    // ]);
    fetch("obj")
      .then(response => response.json())
      .then(response => {
        if (response["status"] === "success") return response["content"]
        throw new Error(response["message"]);
      })
      .then(results => commit("addObjects", results))
      .catch(err => console.error(err));
  },
  setTag({commit}, {object_id, tagName, tagValue}){
    fetch(`obj/${object_id}/tag/${tagName}/${tagValue}`, {method: "PUT"})
      .then(() => {
        commit('setTag', {object_id, tagName, tagValue});
      })
      .catch(err => console.error(`Tag ${tagName} errored on add`, err));
  },
  deleteTag({commit}, {object_id, tagName, tagValue}){
    fetch(`obj/${object_id}/tag/${tagName}/${tagValue}`, {method: "DELETE"})
      .then(() => {
        commit('deleteTag', {object_id, tagName, tagValue});
      })
      .catch(err => console.error(`Tag ${tagName} errored on delete`, err));
  },
  saveName({commit, dispatch}, {object_id, name}) {
    fetch(`obj/${object_id}/name/${name}`, {method: "POST"})
      .then(() => {
        dispatch("getObjects");
      })
  },
  deleteObject({dispatch}, {object_id}){
    return fetch(`obj/${object_id}`, {method: "DELETE"})
      .then(() => {
        dispatch("getObjects");
      });
  },
  newObject({commit, dispatch}, {fileData, name, tags}) {
    let form = new FormData();
    form.append('name', name);
    form.append('file', fileData);
    form.append('tags', JSON.stringify(tags));
    fetch("obj", {method: "PUT", body: form})
      .then(response => {
        if (response["ok"] === false) throw new Error(response["statusText"]);
        return response.json();
      }).then(response => {
        if (response["status"] === "error") throw new Error(response["message"]);
        dispatch("getObjects")
        return response["content"]
      }).catch(error => console.error(error));
  }
}
