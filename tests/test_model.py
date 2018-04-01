import contextlib

import synapse.cores.common as s_cores_common

import synapse.lib.iq as s_iq
import synapse.lib.tufo as s_tufo


class ModelTest(s_iq.SynTest):

    @contextlib.contextmanager
    def getRamCore(self):
        with s_iq.SynTest.getRamCore(self=self) as core:
            core.setConfOpts({'modules': (('ibutton.model.IButtonModel', {}),),
                              'caching': 1,
                              'cache:maxsize': 25000})
            yield core


    def test_model_ibutton(self):
        td = {'serial': '5E00000038013B21', 'block': '3', 'tmnt': 'Control'}
        ed = {'serial': '5e00000038013b21', 'block': 3, 'tmnt': 'control'}
        eprop = 'a14c37660532af1e02e91a2c0cda75f0'

        with self.getRamCore() as core:  # s_cortex_common.Cortex
            node = core.formTufoByProp('ibutton', td)
            _, pprop = s_tufo.ndef(node)
            props = s_tufo.props(node)
            self.eq(pprop, eprop)
            self.eq(props, ed)

        with self.getRamCore() as core:  # s_cortex_common.Cortex
            new_td = td.copy()
            new_td['serial'] = new_td.get('serial').lower()

            node = core.formTufoByProp('ibutton', new_td)
            _, pprop = s_tufo.ndef(node)
            props = s_tufo.props(node)
            self.eq(pprop, eprop)
            self.eq(props, ed)
