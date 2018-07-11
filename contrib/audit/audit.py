#!/usr/bin/python3

import argparse
import gzip
import io
import json
import os
import sys

from collections import OrderedDict

bobRoot = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..')
sys.path.append(bobRoot+"/pym")

from bob.audit import Audit
from bob.errors import BuildError
from bob.utils import asHexStr

def audit():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help="audit file", required=True)
    parser.add_argument('-s', '--sort', help="sort references by [buildId, name]",
            choices=['buildId', 'name'], default='name')

    args = parser.parse_args(sys.argv[1:])

    audit = Audit.fromFile(args.file)

    references = OrderedDict()
    ids = {}
    def prettyDeps(artifact, ids):
        a = artifact.dump()
        deps = a.get("dependencies", {})

        for d in ["args", "tools", "sandbox"]:
            dep = deps.get(d, [])
            if dep:
                if isinstance(dep, list):
                    resolved = []
                    for _d in dep:
                        resolved.append(ids.get(_d))
                    a["dependencies"][d] = sorted(resolved)
                elif isinstance(dep, dict):
                    resolved = OrderedDict()
                    for k,v in dep.items():
                        resolved[k] = ids.get(v)
                    a["dependencies"][d] = resolved
        return a

    def dumpReferences(artifact, audit, ids, references):
        for r in artifact.getReferences():
            ref = audit.getArtifact(r)
            ids[asHexStr(ref.getId())] = ref.getMetaData().get("recipe","") + " ("+ ref.getMetaData().get("step","") + ") " + ref.getMetaData().get("package","") + " " + asHexStr(ref.getBuildId()) + " " + asHexStr(ref.getId())
            dumpReferences(ref, audit, ids, references)
        if (args.sort == 'name'):
            name = artifact.getMetaData().get("recipe","") + " ("+ artifact.getMetaData().get("step","") + ") " + artifact.getMetaData().get("package","")
        elif (args.sort == 'buildId'):
            name = asHexStr(artifact.getBuildId())
        if (name in references):
            if (asHexStr(artifact.getId()) != references[name].get("artifact-id")):
                name += " " + asHexStr(artifact.getId())
        references[name] = prettyDeps(artifact, ids)

    dumpReferences(audit.getArtifact(), audit, ids, references)

    tree = {
        "artifact" : prettyDeps(audit.getArtifact(), ids),
        "references" : references
    }
    print(json.dumps(tree))

if __name__ == '__main__':
    audit()
