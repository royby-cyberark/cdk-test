#!/usr/bin/env python3

from aws_cdk import core

from cdktest.cdktest_stack import CdktestStack


app = core.App()
CdktestStack(app, "cdktest")

app.synth()
