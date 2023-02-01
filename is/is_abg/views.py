from django.shortcuts import render
from django.contrib import messages

from .models import iabgInputForm
from .custom_apps.intersight_rest import intersight_get
from .custom_apps.as_built import create_word_doc_paragraph, create_word_doc_table, create_word_doc_title
import pandas as pd
import os

from .forms import iabgForm


# Create your views here.

def index(request):
    return render(request, 'is_abg/index.html')


def charts(request):
    return render(request, 'is_abg/charts.html')


def broken(request):
    return render(request, 'is_abg/broke.html')


def ua(request):
    return render(request, 'is_abg/utilities-animation.html')


def ub(request):
    return render(request, 'is_abg/utilities-border.html')


def uo(request):
    return render(request, 'is_abg/utilities-other.html')


def uc(request):
    return render(request, 'is_abg/utilities-color.html')


def buttons(request):
    return render(request, 'is_abg/buttons.html')


def cards(request):
    return render(request, 'is_abg/cards.html')


def tables(request):
    return render(request, 'is_abg/tables.html')


def abg(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = iabgForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            for i in iabgInputForm.objects.all():
                i.delete()
            post = form.save(commit=False)
            post.save()
            for i in iabgInputForm.objects.all():
                blade_server = intersight_get(resource_path='/compute/Blades',
                                              host=i.host, private_key=i.private_api_key, public_key=i.public_api_key)

                compute_summary = intersight_get(
                    resource_path='/compute/PhysicalSummaries',
                    host=i.host, private_key=i.private_api_key, public_key=i.public_api_key,
                    query_params={
                        "$select": "AvailableMemory,CpuCapacity,Dn,Firmware,Model,Name,OperPowerState,OperState"
                    })
                rack_server = intersight_get(resource_path='/compute/RackUnits',
                                             host=i.host, private_key=i.private_api_key, public_key=i.public_api_key)
                physical_ports = intersight_get(
                    resource_path='/ether/PhysicalPorts',
                    host=i.host, private_key=i.private_api_key, public_key=i.public_api_key,
                    query_params={
                        "$filter": "OperState eq 'up'",
                        "$orderby": "Dn",
                        "$select": "AggregatePortId,Mode,Dn,OperSpeed,OperState,PeerDn,TransceiverType"
                    })
                fc_ports = intersight_get(resource_path='/fc/PhysicalPorts',
                                          host=i.host, private_key=i.private_api_key,
                                          public_key=i.public_api_key,
                                          query_params={
                                              "$filter": "OperState eq 'up'",
                                              "$orderby": "Dn",
                                              "$select": "PortChannelId,OperSpeed,Dn,Mode,OperState,Wwn"
                                          })
                firmware_running = intersight_get(resource_path='/firmware/RunningFirmwares',
                                                  host=i.host, private_key=i.private_api_key,
                                                  public_key=i.public_api_key,
                                                  query_params={
                                                      "$orderby": "Type",
                                                      "$select": "Dn,Type,Version,PackageVersion,ObjectType,Component"})
                hyperflex_cluster = intersight_get(resource_path='/hyperflex/Clusters',
                                                   host=i.host, private_key=i.private_api_key,
                                                   public_key=i.public_api_key,
                                                   query_params={
                                                       "$select": "Summary"})
                hyperflex_node = intersight_get(resource_path='/hyperflex/Nodes',
                                                host=i.host, private_key=i.private_api_key,
                                                public_key=i.public_api_key,
                                                query_params={
                                                    "$select": "DisplayVersion,HostName,Ip,ModelNumber,Role,SerialNumber,Status,Version"})
                hyperflex_health = intersight_get(resource_path='/hyperflex/Healths',
                                                  host=i.host, private_key=i.private_api_key,
                                                  public_key=i.public_api_key,
                                                  query_params={"$select": "ResiliencyDetails"})

                # Due to new call in the API, ls/ServiceProfiles is deprecated
                # service_profile = intersight_get(resource_path='/ls/ServiceProfiles',
                #     host=i.host, private_key=i.private_api_key,
                #     public_key=i.public_api_key,
                #                     query_params={"$filter": "AssignState eq 'assigned'", "$orderby": "OperState"})
                service_profile = intersight_get(resource_path='/server/Profiles',
                                                 host=i.host, private_key=i.private_api_key,
                                                 public_key=i.public_api_key,
                                                 query_params={"$filter": "AssignedServer ne 'null'",
                                                               "$orderby": "ModTime"})
                management_address = intersight_get(resource_path='/management/Interfaces',
                                                    host=i.host, private_key=i.private_api_key,
                                                    public_key=i.public_api_key,
                                                    query_params={
                                                        "$select": "Dn,Ipv4Address,Ipv4Mask,Ipv4Gateway,MacAddress"})

                if firmware_running == None:
                    return render(request, 'is_abg/broke.html')

                management_df = pd.DataFrame.from_dict(management_address['Results'])
                management_df = management_df.drop(columns=['ClassId', 'Moid', 'ObjectType'], errors='ignore')
                service_profile_df = pd.DataFrame.from_dict(service_profile['Results'])
                service_profile_df = service_profile_df.drop(columns=['ClassId', 'Moid', 'ObjectType',
                                                                      'Owners', 'DeviceMoId', 'DomainGroupMoid',
                                                                      'CreateTime', 'PermissionResources',
                                                                      'RegisteredDevice', 'Rn', 'SharedScope', 'Tags',
                                                                      'ModTime', 'AccountMoid'], errors='ignore')
                hyperflex_health_df = pd.DataFrame.from_dict(hyperflex_health['Results'])
                hyperflex_node_df = pd.DataFrame.from_dict(hyperflex_node['Results'])
                hyperflex_node_df = hyperflex_node_df.drop(columns=['ClassId', 'Moid', 'ObjectType'], errors='ignore')
                hyperflex_cluster_df_list = []
                for i in hyperflex_cluster['Results']:
                    # pp.pprint(i['Summary'])
                    hyperflex_cluster_df = pd.DataFrame.from_dict(i['Summary'])
                    hyperflex_cluster_df = hyperflex_cluster_df.drop(columns=['ClassId', 'ObjectType', 'Boottime',
                                                                              'CompressionSavings',
                                                                              'DeduplicationSavings', 'Downtime',
                                                                              'HealingInfo',
                                                                              'ResiliencyDetails', 'ResiliencyInfo',
                                                                              'ResiliencyDetailsSize', 'TotalSavings'],
                                                                     errors='ignore')
                    hyperflex_cluster_df.drop_duplicates()
                    hyperflex_cluster_df_list.append(hyperflex_cluster_df)

                firmware_running_df = pd.DataFrame.from_dict(firmware_running['Results'])
                firmware_running_df = firmware_running_df.drop(columns=['ClassId', 'Moid', 'ObjectType'],
                                                               errors='ignore')
                fc_ports_df = pd.DataFrame.from_dict(fc_ports['Results'])
                fc_ports_df = fc_ports_df.drop(columns=['ClassId', 'Moid', 'ObjectType'], errors='ignore')
                physical_ports_df = pd.DataFrame.from_dict(physical_ports['Results'])
                physical_ports_df = physical_ports_df.drop(columns=['ClassId', 'Moid', 'ObjectType'], errors='ignore')
                rack_server_df = pd.DataFrame.from_dict(rack_server['Results'])
                compute_summary_df = pd.DataFrame.from_dict(compute_summary['Results'])
                compute_summary_df = compute_summary_df.drop(columns=['ClassId', 'Moid', 'ObjectType'], errors='ignore')
                blade_server_df = pd.DataFrame.from_dict(blade_server['Results'])

                firmware_running_df = pd.DataFrame.from_dict(firmware_running['Results'])
                firmware_running_df = firmware_running_df.drop(columns=['ClassId', 'Moid', 'ObjectType'],
                                                               errors='ignore')
                fc_ports_df = pd.DataFrame.from_dict(fc_ports['Results'])
                fc_ports_df = fc_ports_df.drop(columns=['ClassId', 'Moid', 'ObjectType'], errors='ignore')
                physical_ports_df = pd.DataFrame.from_dict(physical_ports['Results'])
                physical_ports_df = physical_ports_df.drop(columns=['ClassId', 'Moid', 'ObjectType'], errors='ignore')
                rack_server_df = pd.DataFrame.from_dict(rack_server['Results'])
                compute_summary_df = pd.DataFrame.from_dict(compute_summary['Results'])
                compute_summary_df = compute_summary_df.drop(columns=['ClassId', 'Moid', 'ObjectType'], errors='ignore')
                blade_server_df = pd.DataFrame.from_dict(blade_server['Results'])

                doc = create_word_doc_title(doc_title='Introduction')

                # Server overview section
                doc = create_word_doc_paragraph(doc=doc, heading_text='Server Summary')
                doc = create_word_doc_table(doc, compute_summary_df)

                # Firmware
                doc = create_word_doc_paragraph(doc=doc, heading_text='Firmware')
                doc = create_word_doc_table(doc, firmware_running_df)

                # Interfaces section
                doc = create_word_doc_paragraph(doc=doc, heading_text='Physical Ports')
                doc = create_word_doc_table(doc, physical_ports_df)

                doc = create_word_doc_paragraph(doc=doc, heading_text='FC Ports')
                doc = create_word_doc_table(doc, fc_ports_df)

                # HyperFlex Section
                doc = create_word_doc_paragraph(doc=doc, heading_text='HyperFlex Cluster')
                for hyperflex_cluster_unit_df in hyperflex_cluster_df_list:
                    doc = create_word_doc_table(doc, hyperflex_cluster_unit_df)

                doc = create_word_doc_paragraph(doc=doc, heading_text='HyperFlex Node Detail')
                doc = create_word_doc_table(doc, hyperflex_node_df)
                doc = create_word_doc_paragraph(doc=doc, heading_text='HyperFlex Health')
                doc = create_word_doc_table(doc, hyperflex_health_df)

                # Service Profile Section
                doc = create_word_doc_paragraph(doc=doc, heading_text='Service Profiles')
                doc = create_word_doc_table(doc, service_profile_df)

                # Management
                doc = create_word_doc_paragraph(doc=doc, heading_text='Management')
                doc = create_word_doc_table(doc, management_df)
                doc.save(r'staticfiles/mediafiles/intersight_output.docx')

                with pd.ExcelWriter(r'staticfiles/mediafiles/intersight_output.xlsx') as writer:
                    management_df.to_excel(writer, sheet_name='management')
                    service_profile_df.to_excel(writer, sheet_name='service_profile')
                    hyperflex_health_df.to_excel(writer, sheet_name='hyperflex_health')
                    hyperflex_node_df.to_excel(writer, sheet_name='hyperflex_node')
                    for hyperflex_cluster_unit_df in hyperflex_cluster_df_list:
                        sheet_name = 'hyperflex_cluster_' + hyperflex_cluster_unit_df["Name"].values[0]
                        hyperflex_cluster_unit_df.to_excel(writer, sheet_name=sheet_name)
                    firmware_running_df.to_excel(writer, sheet_name='firmware_running')
                    fc_ports_df.to_excel(writer, sheet_name='fc_ports')
                    physical_ports_df.to_excel(writer, sheet_name='physical_ports')
                    rack_server_df.to_excel(writer, sheet_name='rack_server')
                    compute_summary_df.to_excel(writer, sheet_name='compute_summary')
                    blade_server_df.to_excel(writer, sheet_name='blade_server')
            return render(request, 'is_abg/abg.html')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = iabgForm()

    return render(request, 'is_abg/abg.html', {'form': form})
