# -*-coding:utf-8 -*-
"""
:创建时间: 2023/4/5 5:54
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *

from collections import namedtuple
import os

from cpapi.all import *
import cpmel.cmds as cc

from cpform import svg
from cpform.docker import default_docker, popup_menu_docker
from cpform.widget.all import *

import cpmel.cmds as cc


def get_blend_shape_in_history(obj):
    history = cc.ls(cc.listHistory(obj), typ='blendShape')
    return [] if history is None else history


def get_blend_shape_target_index_and_name_list(obj):
    bpfn = MFnBlendShapeDeformer(obj.api1_node_object())
    # bpfn.numWeights()
    weight_index_list = MIntArray()
    bpfn.weightIndexList(weight_index_list)

    w_attr = obj.attr('w')
    return [(i, w_attr[i].name()) for i in weight_index_list]


def get_blend_shape_target_inbetween_index_and_inbetween_weight_list(obj, base_object_index, target_index):
    bpfn = MFnBlendShapeDeformer(obj.api1_node_object())
    # bpfn.numWeights()
    base_object_list = MObjectArray()
    bpfn.getBaseObjects(base_object_list)
    base_object = base_object_list[base_object_index]

    weight_index_list = MIntArray()
    bpfn.targetItemIndexList(target_index, base_object, weight_index_list)

    return [(i, (i - 5000) / 1000) for i in weight_index_list]


# select -add `sculptTarget -e -regenerate true -target 0 -inbetweenWeight 0.6 blendShape1`;

_OptionValue = namedtuple(
    'OptionValue',
    [
        'option_name',
        'blend_shape_node',
        'source_mesh',  # 从什么节点搜索到的
        'base_attr',
        'target_attr',
        'target_index',
        'target_inbetween_index',
        'target_inbetween_weight',
    ],
)


class OptionValue(_OptionValue):
    def obtain_or_create_target_mesh(self):
        """

        :rtype: cc.DagNode
        """
        sel = cc.selected()
        try:
            source_attr = cc.listConnections(self.target_attr, s=True)
            if len(source_attr) > 0:
                return source_attr[0]
            # sculptTarget -e -regenerate true -target 0 -inbetweenWeight 0.6 blendShape1
            if not cc.objExists('DrawBlendShapeGroup'):
                cc.createNode('transform', n='DrawBlendShapeGroup')
            source_node = cc.sculptTarget(
                self.blend_shape_node,
                e=True,
                regenerate=True,
                target=self.target_index,
                inbetweenWeight=self.target_inbetween_weight,
            )[0]
            source_node.hide()
            source_node.parent = 'DrawBlendShapeGroup'

            return source_node
        finally:
            cc.select(sel, r=True)


def get_blend_shape_target_option_list(source_mesh, blend_shape_node):
    for target_index, target_name in get_blend_shape_target_index_and_name_list(blend_shape_node):
        for target_inbetween_index, target_inbetween_weight in get_blend_shape_target_inbetween_index_and_inbetween_weight_list(
                blend_shape_node,
                0,
                target_index):
            # blendShape1.inputTarget[0].inputTargetGroup[0].inputTargetItem[5400].inputGeomTarget
            base_attr = blend_shape_node.attr('input[0].inputGeometry')
            target_attr = blend_shape_node.attr(
                'inputTarget[0].inputTargetGroup[{}].inputTargetItem[{}].inputGeomTarget'.format(
                    target_index,
                    target_inbetween_index,
                )
            )
            option = OptionValue(
                option_name="{} {}".format(target_name, target_inbetween_weight),
                blend_shape_node=blend_shape_node,
                source_mesh=source_mesh,
                base_attr=base_attr,
                target_attr=target_attr,
                target_index=target_index,
                target_inbetween_index=target_inbetween_index,
                target_inbetween_weight=target_inbetween_weight,
            )
            yield option


def find_blend_shape_target_option_list_by_now_selected_object():
    sel = cc.selected()
    sel = set([i.node() if isinstance(i, cc.Component) else i for i in sel])

    option_list = []
    for source_mesh in sel:
        for blend_shape_node in get_blend_shape_in_history(source_mesh):
            for option in get_blend_shape_target_option_list(source_mesh, blend_shape_node):
                option_list.append(option)
    return option_list


def transfer_blend_shape(source_mesh, deformed_mesh, target_mesh, blend_shape_node_name):
    source_blend_shape = get_blend_shape_in_history(source_mesh)[0]
    target_blend_shape = cc.blendShape(target_mesh, n=blend_shape_node_name)[0]
    for target_index, target_name in get_blend_shape_target_index_and_name_list(source_blend_shape):
        for target_inbetween_index, target_inbetween_weight in get_blend_shape_target_inbetween_index_and_inbetween_weight_list(
                source_blend_shape,
                0,
                target_index):
            # # blendShape1.inputTarget[0].inputTargetGroup[0].inputTargetItem[5400].inputGeomTarget
            # base_attr = source_blend_shape.attr('input[0].inputGeometry')
            # target_attr = source_blend_shape.attr(
            #     'inputTarget[0].inputTargetGroup[{}].inputTargetItem[{}].inputGeomTarget'.format(
            #         target_index,
            #         target_inbetween_index,
            #     )
            # )
            # add a bs
            source_attr = cc.new_object(target_name)
            # get input attr
            input_attr = cc.listConnections(source_attr, s=True, d=False, p=True)
            if len(input_attr) > 0:
                cc.disconnectAttr(input_attr[0], source_attr)
            try:
                old_source_value = source_attr.get_value()
                try:
                    source_attr.set_value(target_inbetween_weight)
                    temp_mesh = cc.duplicate(deformed_mesh, rr=True)[0]
                finally:
                    source_attr.set_value(old_source_value)
                try:
                    cc.blendShape(
                        target_blend_shape,
                        edit=True,
                        t=(target_mesh, 1, target_name.split('.')[-1], target_inbetween_weight),
                    )
                    if len(input_attr) > 0:
                        cc.connectAttr(input_attr[0], target_blend_shape.attr(target_name.split('.')[-1]))
                finally:
                    cc.delete(temp_mesh)
            finally:
                if len(input_attr) > 0:
                    cc.connectAttr(input_attr[0], source_attr)


def create_main_window():
    widget = FormLayout(
        childs=[
            'BS源物体', SelectWidget(),
            '变形源物体', SelectWidget(),
            '目标物体', SelectWidget(),
            '新BS节点名称', LineEditWidget(text='blendShape'),
        ],
        align='top',
    )
    help_widget = HelpWidget(r'''
BS源物体: 有BlendShape节点的物体
变形源物体: 有变形效果的物体
目标物体: 被传递BlendShape的物体
''')
    widget = SubmitWidget([widget, help_widget], transfer_blend_shape, doit_text='传递')
    return default_docker(form=widget, name='传递BlendShape工具')


# test
if __name__ == '__main__':
    cc.eval(r'''
polySphere -r 1 -sx 20 -sy 20 -ax 0 1 0 -cuv 2 -ch 1;
// 结果: pSphere1 polySphere1 // 
duplicate -rr;
//结果: pSphere2 //
duplicate -rr;
//结果: pSphere3 //
duplicate -rr;
//结果: pSphere4 //
select -r pSphere1 ;
blendShape -automatic;
// 结果: blendShape1 // 
sculptTarget -e -target -1 blendShape1;
blendShape -e -tc on -t |pSphere1|pSphereShape1 0 pSphere4 1 -w 0 1  blendShape1;
blendShape -e -rtd 0 0 blendShape1;
sculptTarget -e -target 0 blendShape1;
''')
    transfer_blend_shape(cc.new_object('pSphere1'), cc.new_object('pSphere2'), cc.new_object('pSphere3'))
