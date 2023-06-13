#/usr/bin/python3

# BSD 3-Clause License
# 
# Copyright (c) 2023, P.L. Lucas
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import docker
import json
import os
from subprocess import PIPE, Popen
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class DialogEntry(Gtk.Dialog):
    def __init__(self, parent, title, label, only_message=False):
        super().__init__(title=title, transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_default_size(150, 100)
        label = Gtk.Label(label=label)
        box = self.get_content_area()
        box.add(label)
        if not only_message:
            self.entry = Gtk.Entry()
            box.add(self.entry)
        self.show_all()

class Handler:
    def __init__(self, builder):
        self.client = docker.from_env()
        self.builder = builder
        self.compose_path = None
        self.dialog = None

    def show_compose_dialog(self, name, image, volumes, ports, environment):
        if self.dialog == None:
            self.dialog = self.builder.get_object("compose_dialog")
            self.dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.builder.get_object("name_compose_dialog_entry").set_text(name)
        self.builder.get_object("image_compose_dialog_entry").set_text(image)
        volumes_textbuffer = self.builder.get_object("volumes_textbuffer")
        volumes_textbuffer.set_text(volumes)
        ports_textbuffer = self.builder.get_object("ports_textbuffer")
        ports_textbuffer.set_text(ports)
        environment_textbuffer = self.builder.get_object("environment_textbuffer")
        environment_textbuffer.set_text(environment)
        self.dialog.show_all()
        response = self.dialog.run()
        ok = True
        if response == Gtk.ResponseType.OK:
            name = self.builder.get_object("name_compose_dialog_entry").get_text().strip()
            image = self.builder.get_object("image_compose_dialog_entry").get_text().strip()
            volumes = volumes_textbuffer.get_text(volumes_textbuffer.get_start_iter(), volumes_textbuffer.get_end_iter(), True).strip()
            ports = ports_textbuffer.get_text(ports_textbuffer.get_start_iter(), ports_textbuffer.get_end_iter(), True).strip()
            environment = environment_textbuffer.get_text(environment_textbuffer.get_start_iter(), environment_textbuffer.get_end_iter(), True).strip()
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")
            ok = False
        self.dialog.hide()
        return (ok, name, image, volumes, ports, environment)

    def init_compose_tree_view(self):
        tree = self.builder.get_object("compose_tree_view")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Name", renderer, text=0)
        tree.append_column(column)
    
        tree = builder.get_object("compose_tree_view")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Image", renderer, text=1)
        tree.append_column(column)

        tree = builder.get_object("compose_tree_view")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Volumes", renderer, text=2)
        tree.append_column(column)

        tree = builder.get_object("compose_tree_view")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Ports", renderer, text=3)
        tree.append_column(column)

        tree = builder.get_object("compose_tree_view")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Enviroment", renderer, text=4)
        tree.append_column(column)

    def init_images_tree_view(self):
        tree = self.builder.get_object("images_tree_view")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Repository", renderer, text=0)
        tree.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tag", renderer, text=1)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("ID", renderer, text=2)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Created", renderer, text=3)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Size", renderer, text=4)
        tree.append_column(column)
    
    def init_containers_tree_view(self):
        tree = self.builder.get_object("containers_tree_view")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("ID", renderer, text=0)
        column.set_resizable(True)
        column.set_clickable(True)
        tree.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Image", renderer, text=1)
        column.set_resizable(True)
        column.set_clickable(True)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Command", renderer, text=2)
        column.set_resizable(True)
        column.set_clickable(True)
        column.set_expand(False)
        column.set_fixed_width(100)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Status", renderer, text=3)
        column.set_resizable(True)
        column.set_clickable(True)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Ports", renderer, text=4)
        column.set_resizable(True)
        column.set_clickable(True)
        column.set_expand(False)
        column.set_fixed_width(100)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Names", renderer, text=5)
        column.set_resizable(True)
        column.set_clickable(True)
        column.set_expand(False)
        tree.append_column(column)
    
    def update_list(self, button):
        self.update_list_images()
        self.update_list_containers()

    def delete_row(self, store, treepath, treeiter):
        store.remove(treeiter)

    def get_rows(self, store, treepath, treeiter):
        self.tree_iters.append(treeiter)

    def delete_rows(self, store):
        self.tree_iters = []
        store.foreach(self.get_rows)
        for tree_iter in self.tree_iters:
            store.remove(tree_iter)

    def update_list_containers(self):
        containers = self.client.containers.list(all=True)
        containers_liststore = self.builder.get_object("containers_liststore")
        self.delete_rows(containers_liststore)
        for container in containers:
            containers_liststore.append(["{0}".format(container.id)[:12], "{0}".format(container.image), "{0} {1}".format(container.attrs["Path"], container.attrs['Args']), container.status, "{0}".format(container.attrs["NetworkSettings"]["Ports"]), container.name])

    def update_list_images(self):
        images = self.client.images.list()
        images_liststore = self.builder.get_object("images_liststore")
        self.delete_rows(images_liststore)
        for image in images:
            #print(image.attrs)
            for tag in image.tags:
                images_liststore.append(["{0}".format(tag.split(':')[0]),"{0}".format(tag.split(':')[1]),"{0}".format(image.id.split(':')[1][0:12]),image.attrs["Created"], "{0:10.2f} Mb".format(image.attrs["Size"]/1000/1000)])

    def run_command(self, command):
        print(command)
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        dialog = Gtk.MessageDialog(
            transient_for=self.builder.get_object("main_window"),
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=command,
            )
        dialog.format_secondary_text("{0}\n{1}".format(stdout, stderr))
        dialog.run()
        dialog.destroy()

    def run_command_containers_row(self, command):
        containers_tree_view = self.builder.get_object("containers_tree_view")
        model, treeiter = containers_tree_view.get_selection().get_selected()
        if treeiter is not None:
            container = "{0}".format(model[treeiter][0])
            command = command.format(container)
            self.run_command(command)
        self.update_list(None)


    def on_destroy(self, *args):
        print("Destroy")
        Gtk.main_quit()

    def on_run_image(self, button):
        images_tree_view = self.builder.get_object("images_tree_view")
        model, treeiter = images_tree_view.get_selection().get_selected()
        if treeiter is not None:
            image = "{0}:{1}".format(model[treeiter][0], model[treeiter][1])
            command = "docker run -d '{0}'".format(image)
            print(command)
            os.system(command)

    def on_delete_image(self, button):
        images_tree_view = self.builder.get_object("images_tree_view")
        model, treeiter = images_tree_view.get_selection().get_selected()
        if treeiter is not None:
            dialog = DialogEntry(self.builder.get_object("main_window"), "Delete item", "¿Delete item?", True)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                image = "{0}:{1}".format(model[treeiter][0], model[treeiter][1])
                command = "docker rmi '{0}'".format(image)
                self.run_command(command)
            dialog.destroy()
        self.update_list(None)

    def on_run_shell_image(self, button):
        images_tree_view = self.builder.get_object("images_tree_view")
        model, treeiter = images_tree_view.get_selection().get_selected()
        if treeiter is not None:
            image = "{0}:{1}".format(model[treeiter][0], model[treeiter][1])
            command = "konsole -e docker run -it '{0}' &".format(image)
            print(command)
            os.system(command)

    def on_pull_image(self, button):
        dialog = DialogEntry(self.builder.get_object("main_window"), "Pull image", "Image name:")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            image = dialog.entry.get_text()
            command = "konsole -e docker pull '{0}'".format(image)
            os.system(command)
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")
        dialog.destroy()
        self.update_list(None)

    def on_delete_container(self, button):
        dialog = DialogEntry(self.builder.get_object("main_window"), "Delete item", "¿Delete item?", True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.run_command_containers_row("docker rm '{0}'")
            self.update_list(None)
        dialog.destroy()
    
    def on_stop_container(self, button):
        self.run_command_containers_row("docker stop '{0}'")
        self.update_list(None)

    def on_restart_container(self, button):
        self.run_command_containers_row("docker restart '{0}'")
        self.update_list(None)

    def on_pause_container(self, button):
        self.run_command_containers_row("docker pause '{0}'")
        self.update_list(None)

    def on_shell_container(self, button):
        containers_tree_view = self.builder.get_object("containers_tree_view")
        model, treeiter = containers_tree_view.get_selection().get_selected()
        if treeiter is not None:
            container = "{0}".format(model[treeiter][0])
            #command = "docker start '{0}'".format(container)
            #print(command)
            #os.system(command)
            command = "konsole -e docker exec -it '{0}' sh &".format(container)
            print(command)
            os.system(command)
            self.update_list(None)

    def on_log_container(self, button):
        containers_tree_view = self.builder.get_object("containers_tree_view")
        model, treeiter = containers_tree_view.get_selection().get_selected()
        if treeiter is not None:
            container = "{0}".format(model[treeiter][0])
            command = "konsole -e docker logs -f '{0}' &".format(container)
            print(command)
            os.system(command)
            self.update_list(None)

    def on_add_compose(self, button):
        (ok, name, image, volumes, ports, environment) = self.show_compose_dialog("", "", "", "", "")
        if ok:
            compose_liststore = self.builder.get_object("compose_liststore")
            compose_liststore.append([name, image, volumes, ports, environment])

    def on_delete_compose(self, button):
        compose_tree_view = self.builder.get_object("compose_tree_view")
        model, treeiter = compose_tree_view.get_selection().get_selected()
        if treeiter is not None:
            dialog = DialogEntry(self.builder.get_object("main_window"), "Delete item", "¿Delete item?", True)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                compose_liststore = builder.get_object("compose_liststore")
                compose_liststore.remove(treeiter)
            elif response == Gtk.ResponseType.CANCEL:
                print("The Cancel button was clicked")
            dialog.destroy()

    def get_compose_items(self):
        self.tree_iters = []
        compose_liststore = self.builder.get_object("compose_liststore")
        compose_liststore.foreach(self.get_rows)
        items = []
        for tree_iter in self.tree_iters:
            name = compose_liststore[tree_iter][0]
            image = compose_liststore[tree_iter][1] 
            volumes = compose_liststore[tree_iter][2] 
            ports = compose_liststore[tree_iter][3] 
            environment = compose_liststore[tree_iter][4]
            items.append({"name": name, "image": image, "volumes": volumes, "ports": ports, "environment": environment})
        return items

    def on_save_compose(self, button):
        dialog = Gtk.FileChooserDialog(title="Please choose a folder", parent=self.builder.get_object("main_quit"), action=Gtk.FileChooserAction.SELECT_FOLDER)
        if self.compose_path != None:
            dialog.set_filename(self.compose_path)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self.compose_path = dialog.get_filename()
            items = self.get_compose_items()
            items_json = json.dumps(items)
            fout = open('{0}/docker-compose.json'.format(dialog.get_filename()), "w")
            fout.write(items_json)
            fout.close()
            fout = open('{0}/docker-compose.yaml'.format(dialog.get_filename()), "w")
            fout.write('version: "3.7"\nservices:\n')
            for item in items:
                fout.write("  {0}:\n".format(item["name"]))
                fout.write("    image: {0}\n".format(item["image"]))
                if len(item["volumes"]) > 0:
                    fout.write("    volumes:\n")
                    for volume in item["volumes"].split('\n'):
                        fout.write("      - {0}\n".format(volume))
                if len(item["ports"]) > 0:
                    fout.write("    ports:\n")
                    for port in item["ports"].split('\n'):
                        fout.write("      - {0}\n".format(port))
                if len(item["environment"]) > 0:
                    fout.write("    environment:\n")
                    for env in item["environment"].split('\n'):
                        fout.write("      {0}\n".format(env))
            fout.close()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    def on_new_compose(self, button):
        compose_liststore = self.builder.get_object("compose_liststore")
        self.delete_rows(compose_liststore)
        self.compose_path = None

    def on_open_compose(self, button):
        dialog = Gtk.FileChooserDialog(title="Please choose a folder", parent=self.builder.get_object("main_quit"), action=Gtk.FileChooserAction.SELECT_FOLDER)
        if self.compose_path != None:
            dialog.set_filename(self.compose_path)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self.compose_path = dialog.get_filename()
            self.on_new_compose(None)
            fin = open('{0}/docker-compose.json'.format(dialog.get_filename()), "r")
            items_json = fin.read()
            fin.close()
            items = json.loads(items_json)
            compose_liststore = self.builder.get_object("compose_liststore")
            for item in items:
                compose_liststore.append([item["name"], item["image"], item["volumes"], item["ports"], item["environment"]])
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    def on_run_compose(self, button):
        self.on_save_compose(button)
        command = 'cd "{0}" ; docker-compose up --remove-orphans -d'.format(self.compose_path)
        print(command)
        os.system(command)
        self.update_list(None)

    def on_stop_compose(self, button):
        command = 'cd "{0}" ; docker-compose down'.format(self.compose_path)
        print(command)
        os.system(command)
        self.update_list(None)

    def on_edit_compose(self, button):
        compose_tree_view = self.builder.get_object("compose_tree_view")
        model, treeiter = compose_tree_view.get_selection().get_selected()
        if treeiter is not None:
            name = model[treeiter][0]
            image = model[treeiter][1] 
            volumes = model[treeiter][2] 
            ports = model[treeiter][3] 
            environment = model[treeiter][4]
            (ok, name, image, volumes, ports, environment) = self.show_compose_dialog(name, image, volumes, ports, environment)
            if ok:
                model[treeiter][0] = name
                model[treeiter][1] = image
                model[treeiter][2] = volumes
                model[treeiter][3] = ports
                model[treeiter][4] = environment

builder = Gtk.Builder()
builder.add_from_string("""
<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated with glade 3.38.2 -->
<interface>
  <requires lib="gtk+" version="3.24"/>
  <object class="GtkListStore" id="compose_liststore">
    <columns>
      <!-- column-name Name -->
      <column type="gchararray"/>
      <!-- column-name Image -->
      <column type="gchararray"/>
      <!-- column-name Volumes -->
      <column type="gchararray"/>
      <!-- column-name Ports -->
      <column type="gchararray"/>
      <!-- column-name Environment -->
      <column type="gchararray"/>
    </columns>
  </object>
  <object class="GtkListStore" id="containers_liststore">
    <columns>
      <!-- column-name ID -->
      <column type="gchararray"/>
      <!-- column-name Image -->
      <column type="gchararray"/>
      <!-- column-name Command -->
      <column type="gchararray"/>
      <!-- column-name Status -->
      <column type="gchararray"/>
      <!-- column-name Ports -->
      <column type="gchararray"/>
      <!-- column-name Names -->
      <column type="gchararray"/>
    </columns>
  </object>
  <object class="GtkTextBuffer" id="environment_textbuffer"/>
  <object class="GtkListStore" id="images_liststore">
    <columns>
      <!-- column-name Repository -->
      <column type="gchararray"/>
      <!-- column-name Tag -->
      <column type="gchararray"/>
      <!-- column-name ID -->
      <column type="gchararray"/>
      <!-- column-name Created -->
      <column type="gchararray"/>
      <!-- column-name Size -->
      <column type="gchararray"/>
    </columns>
  </object>
  <object class="GtkWindow" id="main_window">
    <property name="can-focus">False</property>
    <property name="title" translatable="yes">Simple docker GUI (sdg)</property>
    <signal name="delete-event" handler="on_destroy" swapped="no"/>
    <signal name="destroy-event" handler="on_destroy" swapped="no"/>
    <child>
      <object class="GtkBox">
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="orientation">vertical</property>
        <child>
          <object class="GtkNotebook">
            <property name="visible">True</property>
            <property name="can-focus">True</property>
            <child>
              <object class="GtkBox">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="orientation">vertical</property>
                <child>
                  <object class="GtkBox">
                    <property name="visible">True</property>
                    <property name="can-focus">False</property>
                    <child>
                      <object class="GtkButton" id="pull_image_button">
                        <property name="label" translatable="yes">Pull</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_pull_image" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">0</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="delete_image_button">
                        <property name="label" translatable="yes">Delete</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_delete_image" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">1</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="run_image_button">
                        <property name="label" translatable="yes">Run</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_run_image" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">2</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="shell_image_button">
                        <property name="label" translatable="yes">Shell</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_run_shell_image" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">3</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="refresh_images_button">
                        <property name="label" translatable="yes">Refresh</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="activate" handler="update_list" swapped="no"/>
                        <signal name="clicked" handler="update_list" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="pack-type">end</property>
                        <property name="position">4</property>
                      </packing>
                    </child>
                  </object>
                  <packing>
                    <property name="expand">False</property>
                    <property name="fill">True</property>
                    <property name="position">0</property>
                  </packing>
                </child>
                <child>
                  <object class="GtkTreeView" id="images_tree_view">
                    <property name="visible">True</property>
                    <property name="can-focus">True</property>
                    <property name="model">images_liststore</property>
                    <property name="reorderable">True</property>
                    <child internal-child="selection">
                      <object class="GtkTreeSelection"/>
                    </child>
                  </object>
                  <packing>
                    <property name="expand">True</property>
                    <property name="fill">True</property>
                    <property name="position">1</property>
                  </packing>
                </child>
              </object>
            </child>
            <child type="tab">
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Images</property>
              </object>
              <packing>
                <property name="tab-fill">False</property>
              </packing>
            </child>
            <child>
              <object class="GtkBox">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="orientation">vertical</property>
                <child>
                  <object class="GtkBox">
                    <property name="visible">True</property>
                    <property name="can-focus">False</property>
                    <child>
                      <object class="GtkButton" id="restart_container_button">
                        <property name="label" translatable="yes">Restart</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_restart_container" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">0</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="stop_container_button">
                        <property name="label" translatable="yes">Stop</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_stop_container" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">1</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="pause_container_button">
                        <property name="label" translatable="yes">Pause</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_pause_container" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">2</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="shell_container_button">
                        <property name="label" translatable="yes">Shell</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_shell_container" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">3</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="log_container">
                        <property name="label" translatable="yes">Log</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_log_container" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">4</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="refresh_containers_button">
                        <property name="label" translatable="yes">Refresh</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="update_list" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="pack-type">end</property>
                        <property name="position">5</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="delete_container_button">
                        <property name="label" translatable="yes">Delete</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_delete_container" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">6</property>
                      </packing>
                    </child>
                  </object>
                  <packing>
                    <property name="expand">False</property>
                    <property name="fill">True</property>
                    <property name="position">0</property>
                  </packing>
                </child>
                <child>
                  <object class="GtkTreeView" id="containers_tree_view">
                    <property name="visible">True</property>
                    <property name="can-focus">True</property>
                    <property name="hscroll-policy">natural</property>
                    <property name="model">containers_liststore</property>
                    <property name="hover-expand">True</property>
                    <child internal-child="selection">
                      <object class="GtkTreeSelection"/>
                    </child>
                  </object>
                  <packing>
                    <property name="expand">True</property>
                    <property name="fill">True</property>
                    <property name="position">1</property>
                  </packing>
                </child>
              </object>
              <packing>
                <property name="position">1</property>
              </packing>
            </child>
            <child type="tab">
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Containers</property>
              </object>
              <packing>
                <property name="position">1</property>
                <property name="tab-fill">False</property>
              </packing>
            </child>
            <child>
              <object class="GtkBox">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="orientation">vertical</property>
                <child>
                  <object class="GtkBox">
                    <property name="visible">True</property>
                    <property name="can-focus">False</property>
                    <child>
                      <object class="GtkButton" id="new_compose:button">
                        <property name="label" translatable="yes">New</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_new_compose" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">0</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="open_compose_button">
                        <property name="label" translatable="yes">Open</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_open_compose" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">1</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="save_compose_button">
                        <property name="label" translatable="yes">Save</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_save_compose" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">2</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkSeparator">
                        <property name="visible">True</property>
                        <property name="can-focus">False</property>
                        <property name="margin-start">8</property>
                        <property name="margin-end">8</property>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">3</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="add_compose_button">
                        <property name="label" translatable="yes">Add</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_add_compose" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">4</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="delete_compose_button">
                        <property name="label" translatable="yes">Delete</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_delete_compose" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">5</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="edit_compose_button">
                        <property name="label" translatable="yes">Edit</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_edit_compose" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">6</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkSeparator">
                        <property name="visible">True</property>
                        <property name="can-focus">False</property>
                        <property name="margin-start">8</property>
                        <property name="margin-end">8</property>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">7</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="run_compose_button">
                        <property name="label" translatable="yes">Run</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_run_compose" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">8</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="stop_compose_button">
                        <property name="label" translatable="yes">Stop</property>
                        <property name="visible">True</property>
                        <property name="can-focus">True</property>
                        <property name="receives-default">True</property>
                        <signal name="clicked" handler="on_stop_compose" swapped="no"/>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">9</property>
                      </packing>
                    </child>
                  </object>
                  <packing>
                    <property name="expand">False</property>
                    <property name="fill">True</property>
                    <property name="position">0</property>
                  </packing>
                </child>
                <child>
                  <object class="GtkTreeView" id="compose_tree_view">
                    <property name="visible">True</property>
                    <property name="can-focus">True</property>
                    <property name="model">compose_liststore</property>
                    <child internal-child="selection">
                      <object class="GtkTreeSelection"/>
                    </child>
                  </object>
                  <packing>
                    <property name="expand">True</property>
                    <property name="fill">True</property>
                    <property name="position">1</property>
                  </packing>
                </child>
              </object>
              <packing>
                <property name="position">2</property>
              </packing>
            </child>
            <child type="tab">
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Composer</property>
              </object>
              <packing>
                <property name="position">2</property>
                <property name="tab-fill">False</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">True</property>
            <property name="fill">True</property>
            <property name="position">1</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
  <object class="GtkTextBuffer" id="ports_textbuffer"/>
  <object class="GtkTextBuffer" id="volumes_textbuffer"/>
  <object class="GtkDialog" id="compose_dialog">
    <property name="can-focus">False</property>
    <property name="title" translatable="yes">Compose item dialog</property>
    <property name="type-hint">dialog</property>
    <child internal-child="vbox">
      <object class="GtkBox">
        <property name="can-focus">False</property>
        <property name="orientation">vertical</property>
        <property name="spacing">2</property>
        <child internal-child="action_area">
          <object class="GtkButtonBox">
            <property name="can-focus">False</property>
            <property name="layout-style">end</property>
            <child>
              <placeholder/>
            </child>
            <child>
              <placeholder/>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">False</property>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
          <!-- n-columns=3 n-rows=5 -->
          <object class="GtkGrid">
            <property name="visible">True</property>
            <property name="can-focus">False</property>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Name:</property>
              </object>
              <packing>
                <property name="left-attach">0</property>
                <property name="top-attach">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkEntry" id="name_compose_dialog_entry">
                <property name="visible">True</property>
                <property name="can-focus">True</property>
              </object>
              <packing>
                <property name="left-attach">1</property>
                <property name="top-attach">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Image:</property>
              </object>
              <packing>
                <property name="left-attach">0</property>
                <property name="top-attach">1</property>
              </packing>
            </child>
            <child>
              <object class="GtkEntry" id="image_compose_dialog_entry">
                <property name="visible">True</property>
                <property name="can-focus">True</property>
              </object>
              <packing>
                <property name="left-attach">1</property>
                <property name="top-attach">1</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Volumes:</property>
              </object>
              <packing>
                <property name="left-attach">0</property>
                <property name="top-attach">2</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Ports:</property>
              </object>
              <packing>
                <property name="left-attach">0</property>
                <property name="top-attach">3</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Environment:</property>
              </object>
              <packing>
                <property name="left-attach">0</property>
                <property name="top-attach">4</property>
              </packing>
            </child>
            <child>
              <object class="GtkScrolledWindow">
                <property name="visible">True</property>
                <property name="can-focus">True</property>
                <property name="shadow-type">in</property>
                <child>
                  <object class="GtkTextView" id="environment_text_view">
                    <property name="visible">True</property>
                    <property name="can-focus">True</property>
                    <property name="buffer">environment_textbuffer</property>
                  </object>
                </child>
              </object>
              <packing>
                <property name="left-attach">1</property>
                <property name="top-attach">4</property>
              </packing>
            </child>
            <child>
              <object class="GtkScrolledWindow">
                <property name="visible">True</property>
                <property name="can-focus">True</property>
                <property name="shadow-type">in</property>
                <child>
                  <object class="GtkTextView" id="ports_compose_dialog_text_view">
                    <property name="visible">True</property>
                    <property name="can-focus">True</property>
                    <property name="buffer">ports_textbuffer</property>
                  </object>
                </child>
              </object>
              <packing>
                <property name="left-attach">1</property>
                <property name="top-attach">3</property>
              </packing>
            </child>
            <child>
              <object class="GtkScrolledWindow">
                <property name="visible">True</property>
                <property name="can-focus">True</property>
                <property name="shadow-type">in</property>
                <child>
                  <object class="GtkTextView" id="volumes_compose_dialog_text_view">
                    <property name="visible">True</property>
                    <property name="can-focus">True</property>
                    <property name="buffer">volumes_textbuffer</property>
                  </object>
                </child>
              </object>
              <packing>
                <property name="left-attach">1</property>
                <property name="top-attach">2</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Put lines with format:
  Host path:Container path
Examples:
  ./database:/var/lib/mysql
  /home/user/etc:/etc
---------------------------------------------</property>
              </object>
              <packing>
                <property name="left-attach">2</property>
                <property name="top-attach">2</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Put lines with format:
  Host port:Container port
Examples:
  8080:80
  2022:22
---------------------------------------------</property>
              </object>
              <packing>
                <property name="left-attach">2</property>
                <property name="top-attach">3</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">Put lines with format:
  Name: Value
Examples:
  MARIADB_USER: admin
  MARIADB_PASSWORD: admin-password
  MARIADB_ROOT_PASSWORD: root-password</property>
              </object>
              <packing>
                <property name="left-attach">2</property>
                <property name="top-attach">4</property>
              </packing>
            </child>
            <child>
              <placeholder/>
            </child>
            <child>
              <placeholder/>
            </child>
          </object>
          <packing>
            <property name="expand">True</property>
            <property name="fill">True</property>
            <property name="position">1</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
</interface>
""")
handler = Handler(builder)
builder.connect_signals(handler)

window = builder.get_object("main_window")
window.set_default_size(300, 400)
handler.init_images_tree_view()
handler.init_containers_tree_view()
handler.init_compose_tree_view()
handler.update_list(None)
window.show_all()
Gtk.main() 
