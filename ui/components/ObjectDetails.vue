<template>
  <section class="media-content">
    <div class="columns">
      <div class="column">
        <b-field label="Name" :type="nameChanged?(nameError?'is-danger':'is-success'):''" label-position="on-border">
          <b-input v-model="name" />
        </b-field>
        <b-notification type="is-primary" :closable="false">
          <b>Metadata</b>
          <ul>
            <li><b>Size: </b>{{ this.formatSize(object.size) }}</li>
            <li><b>Last Updated: </b>{{ object.updated }}</li>
          </ul>
        </b-notification>
      </div>
      <div class="column">
        <TagManager :object_id="object.id" :tags="object.metadata"/>
      </div>
    </div>
    <footer>
      <b-button type="is-primary" :disabled="!nameChanged||nameError" @click="saveName">Save</b-button>
      <b-button type="is-light" @click="closeMe">Close</b-button>
    </footer>
  </section>
</template>

<script>

import humanReadable from "../modules/common";

export default {
  name: "ObjectDetails",
  props: {
    object: Object,
  },
  data() {return {
    name: "",
    nameError: false,
    hasChanged: false
  }},
  watch: {
    name: function() {
      let _t = this;
      fetch(`obj/name/${this.name}`)
        .then(response => response.json())
        .then(response => response["content"])
        .then(content => _t.nameError = content !== null)
    }
  },
  computed: {
    nameChanged: function(){return this.name !== this.object.name}
  },
  methods: {
    formatSize: (size) => humanReadable(size),
    saveName: function(){
      this.$store.dispatch('saveName', {object_id: this.object.id, name: this.name});
      this.closeMe();
    },
    closeMe: function(){
      this.$emit('close-detail', this.object);
    }
  },
  async fetch(){
    this.name = this.object.name;
  }
}
</script>

<style scoped>

</style>
