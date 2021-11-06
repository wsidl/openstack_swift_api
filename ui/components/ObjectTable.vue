<template>
  <div class="container">
    <nav class="level container">
      <div class="level-left">
        <div class="level-item">
          <b-field label="Search" label-position="on-border" >
            <b-input name="search" v-model="searchTerm" expanded/>
          </b-field>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <b-button type="is-primary" @click="showNewObject=true">New</b-button>
        </div>
      </div>
      <b-modal v-model="showNewObject">
        <div class="card">
          <div class="card-content">
            <b-field label="File to attach">
              <b-input type="file" placeholder="Attach local file" v-model="newFile"></b-input>
            </b-field>
            <b-field label="Name">
              <b-input type="input" v-model="newName"></b-input>
            </b-field>
            <b-field grouped group-multiline>
              <b-button type="is-primary" @click="saveObject">Save</b-button>
            </b-field>
          </div>
        </div>
      </b-modal>
    </nav>
    <b-table ref="objectTable" striped :data="objects" detailed detail-transition="fade" >
      <b-table-column id="id" label="ID" width="40" numeric v-slot="props">
        {{ props.row.id }}
      </b-table-column>
      <b-table-column id="name" field="name" label="Name" sortable v-slot="props">
        <template>
          <a @click="props.toggleDetails(props.row)">
            {{ props.row.name }}
          </a>
        </template>
      </b-table-column>
      <b-table-column id="size" field="size" label="Size" width="120" numeric sortable v-slot="props">
        {{ formatSize(props.row.size) }}
      </b-table-column>
      <b-table-column id="tags" label="Tags" width="90" numeric v-slot="props">
        {{ props.row.metadata.length }} tags
      </b-table-column>
      <b-table-column label="Actions" width="90" v-slot="props">
        <field>

          <b-button type="is-primary is-inverted" size="is-small" @click="downloadObject(props.row.id)">
            <b-icon icon="download"/>
          </b-button>
          <b-button type="is-danger is-inverted" size="is-small" @click="deleteObject(props.row.id)">
            <b-icon icon="delete"/>
          </b-button>
        </field>
      </b-table-column>
      <template #detail="deets">
        <article class="media">
          <ObjectDetails :object="deets.row" @close-detail="closeDetail"/>
        </article>
      </template>
    </b-table>
  </div>
</template>

<script>

import humanReadable from "../modules/common";
const sep = ".";

export default {
  data() {return {
    showNewObject: false,
    newFile: '',
    extension: '',
    newName: '',
    searchTerm: ''
  }},
  watch: {
    newFile: function(){
      let fileParts = this.newFile.split('\\');
      let fileName = fileParts[fileParts.length - 1];
      fileParts = fileName.split(sep)
      this.extension = fileParts[fileParts.length - 1];
      this.newName = fileParts.slice(0, fileParts.length - 1).join(sep);
    },
  },
  computed: {
    objects (){
      if(this.searchTerm.length===0)return this.$store.state.objects;
      return this.$store.state.objects.filter(
        o => o.name.includes(this.searchTerm)
      )
    }
  },
  methods: {
    formatSize: function(size){return humanReadable(size)},
    closeDetail: function(object){this.$refs.objectTable.closeDetailRow(object)},
    deleteObject: function(object_id){
      this.$store.dispatch("deleteObject", {object_id: object_id});
    },
    saveObject: function(){
      this.$store.dispatch('newObject', {
        fileData: document.querySelector('input[type="file"]').files[0],
        name: this.newName, tags: [["format", this.extension]]
      });
      this.newName = "";
      this.newFile = "";
      this.extension = "";
      this.showNewObject = false;
    },
    downloadObject: function(object_id){
      window.open(`obj/${object_id}/download`, '_self');
    }
  },
  mounted() {
    this.$store.dispatch("getObjects");
  }
}
</script>

<style scoped>
  .even {background-color: #ddd}
  .odd {background-color: #fff}
</style>
