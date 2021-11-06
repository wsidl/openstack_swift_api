<template>
  <div>
    <b-field grouped group-multiline>
      <div class="control" v-for="meta in tags">
        <b-taglist attached>
          <b-tag type="is-primary">{{ meta[0] }}</b-tag>
          <b-tag type="is-dark" closable close-type="is-primary" @close="deleteTag(meta)">{{ meta[1] }}</b-tag>
        </b-taglist>
      </div>
    </b-field>
    <b-field label="New Tag" v-if="!show_value" label-position="on-border">
      <b-autocomplete icon-right-clickable :icon-right="new_tag.length>0?'arrow-right':''" v-model="new_tag" @icon-right-click="toggleTag" @keyup.native.enter="toggleTag" :data="tagNames"></b-autocomplete>
    </b-field>
    <b-field label="Tag Value" v-if="show_value" label-position="on-border">
      <b-autocomplete icon-right-clickable :icon-right="new_value.length>0?'arrow-right':''" v-model="new_value" @icon-right-click="saveTag" @keyup.native.enter="saveTag" :data="tagValues"></b-autocomplete>
    </b-field>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: "TagManager",
  data() {return {
    new_tag: '',
    show_value: false,
    new_value: '',
    tagNames: [],
    tagValues: []
  }},
  props: {
    tags: Array,
    object_id: Number
  },
  watch: {
    new_tag: function(){
      let _t = this;
      fetch(`tags?search=${this.new_tag}`)
        .then(response => response.json())
        .then(function(r){_t.tagNames = r["content"]})
    },
    new_value: function(){
      let _t = this;
      fetch(`tags/${this.new_tag}?search=${this.new_value}`)
        .then(response => response.json())
        .then(function(r){_t.tagValues = r["content"]})
    },
  },
  methods: {
    toggleTag: function(){
      this.show_value = !this.show_value
    },
    saveTag: function(){
      this.$store.dispatch('setTag', {object_id: this.object_id, tagName: this.new_tag, tagValue: this.new_value});
      this.new_tag = '';
      this.new_value = '';
      this.toggleTag();
    },
    deleteTag: function([tag, value]){
      this.$store.dispatch('deleteTag', {object_id: this.object_id, tagName: tag, tagValue: value});
    }
  }
}
</script>

<style scoped>

</style>
